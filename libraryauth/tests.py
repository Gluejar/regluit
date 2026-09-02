import os
from io import StringIO
from types import SimpleNamespace
from unittest import mock

from bs4 import BeautifulSoup
from django.urls import reverse
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.core import mail
from django.core.cache import cache
from django.core.management import call_command
from django.template.loader import render_to_string
from social_django.models import UserSocialAuth

from .management.commands.email_google_users_set_password import (
    SEND_ENV_VAR, find_candidates,
)


class TestLibraryAuth(TestCase):
    fixtures = ['initial_data.json']
    def setUp(self):
        pass

    def test_login(self):
        resp = self.client.get(reverse('superlogin'), data={'next': '/'})
        self.assertEqual(200, resp.status_code)
        self.client.cookies['un'] = 'bob'
        resp = self.client.get(reverse('superlogin'), data={'next': '/'})
        self.assertEqual(200, resp.status_code)
        resp = self.client.post(reverse('superlogin'), data={'username': 'bob'})
        self.assertEqual(200, resp.status_code)

    def test_pages(self):
        resp = self.client.get(reverse('registration_register'))
        self.assertEqual(200, resp.status_code)

    def test_registration(self):
        """
        LibraryAuth Registration creates a new inactive account and a new profile
        with activation key, populates the correct account data and
        sends an activation email.

        """
        encode_answers = cache.get('encode_answers')
        resp = self.client.post(reverse('registration_register'),
                                data={'username': 'bob',
                                      'email': 'bob@example.com',
                                      'password1': 'secret',
                                      'password2': 'secret',
                                      'notarobot': '11',
                                      'tries': str(encode_answers.get(11)),
                                      })
        self.assertRedirects(resp, reverse('registration_complete'))

        new_user = User.objects.get(username='bob')

        self.assertTrue(new_user.check_password('secret'))
        self.assertEqual(new_user.email, 'bob@example.com')

        # New user must not be active.
        self.assertFalse(new_user.is_active)

    def test_bad_registration(self):
        """
        LibraryAuth Registration rejects.

        """
        resp = self.client.post(reverse('registration_register'),
                                data={'username': 'badbob',
                                      'email': 'bob@mailnesia.com',
                                      'password1': 'secret',
                                      'password2': 'secret'})
        self.assertTrue('Please supply a permanent email address' in str(resp.content, 'utf-8'))

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username='badbob')

    def test_is_disposable(self):
        from .emailcheck import is_disposable
        self.assertFalse(is_disposable('eric@hellman.net'))
        self.assertTrue(is_disposable('eric@mailnesia.com'))


class TestAppConfigSignalsWired(TestCase):
    """Regression guard for issue #1175.

    Django 4.1 removed `default_app_config`, and an AppConfig defined in an app's
    __init__.py is NOT auto-discovered (Django only scans <app>/apps.py). When that
    regression bit during the 4.2 cutover, LibraryAuthConfig.ready() stopped running
    and signals.py was never imported. These tests fail if the config ever moves back
    out of apps.py or otherwise stops being the active config.
    """

    def test_appconfig_is_discovered(self):
        from django.apps import apps
        from regluit.libraryauth.apps import LibraryAuthConfig
        self.assertIsInstance(apps.get_app_config('libraryauth'), LibraryAuthConfig)

    def test_user_activated_receiver_connected(self):
        # ready() must have imported signals.py and connected the dedup receiver.
        from django_registration.signals import user_activated
        names = []
        for entry in user_activated.receivers:
            # Django <5.0: (lookup_key, receiver); Django >=5.0: (lookup_key, receiver, is_async)
            ref = entry[1]
            fn = ref if getattr(ref, '__name__', None) else (ref() if callable(ref) else None)
            names.append(getattr(fn, '__name__', None))
        self.assertIn('handle_same_email_account', names)


class TestLogoutView(TestCase):
    """Regression guard for the logout-405 incident (2026-08-29).

    Django 5.0 removed GET support from django.contrib.auth.views.LogoutView
    (deprecated in 4.1, flagged as a known follow-up in PR #1145, never
    fixed). The 5.2 upgrade (PR #1203, live in prod 2026-08-26) exposed it:
    every "Sign Out" / "log out" link in the site was a plain GET <a>, so
    /accounts/logout/ started 405ing for real users. Fixed by turning those
    links into POST forms (base.html's nav, gift_user_error.html,
    pledge_user_error.html). These tests would have caught it.
    """
    fixtures = ['initial_data.json']

    # A bare TemplateView (no view-layer business logic / DB lookups) that
    # still extends base.html -- lets these tests exercise the real nav
    # markup without depending on unrelated data (e.g. the homepage's
    # featured-campaign query).
    NAV_PAGE = '/accounts/superlogin/welcome/'

    def setUp(self):
        self.user = User.objects.create_user('logouttester', 'logouttester@example.org', 'secret')

    def test_get_is_405(self):
        # Documents the Django 5.0 behavior change itself, independent of
        # any of this app's templates.
        resp = self.client.get(reverse('logout'))
        self.assertEqual(405, resp.status_code)
        self.assertIn('POST', resp['Allow'])

    def test_post_logs_out_and_redirects(self):
        self.client.login(username='logouttester', password='secret')
        resp = self.client.post(reverse('logout'))
        self.assertEqual(302, resp.status_code)
        # Session should no longer be authenticated.
        resp = self.client.get(self.NAV_PAGE)
        self.assertFalse(resp.wsgi_request.user.is_authenticated)

    def test_post_honors_next(self):
        self.client.login(username='logouttester', password='secret')
        resp = self.client.post(reverse('logout'), data={'next': '/some/safe/path/'})
        self.assertRedirects(resp, '/some/safe/path/', fetch_redirect_response=False)

    def test_post_rejects_external_next_as_open_redirect(self):
        # RedirectURLMixin validates 'next' against the request's own host
        # and scheme -- a POST logout must not become an open redirect via
        # a crafted next= pointing off-site. This is Django's own guard
        # (url_has_allowed_host_and_scheme), exercised here through this
        # app's actual settings/URLconf as a regression/documentation test.
        #
        # Assert equality with the exact safe fallback (LOGOUT_REDIRECT_URL
        # = '/'), not just "doesn't contain the evil hostname" -- a looser
        # substring check would miss a bypass that lands somewhere else
        # unsafe without literally containing that string (CC review,
        # 2026-08-29).
        self.client.login(username='logouttester', password='secret')
        resp = self.client.post(reverse('logout'), data={'next': 'https://evil.example.com/phish'})
        self.assertRedirects(resp, '/', fetch_redirect_response=False)

    def test_authenticated_nav_sign_out_is_a_post_form_not_a_get_link(self):
        # Renders base.html's authenticated nav and checks the "Sign Out"
        # control POSTs -- with a real method="post" and a CSRF token, not
        # just *some* form -- rather than being a plain
        # <a href="/accounts/logout/"> (the exact shape of the original bug).
        self.client.login(username='logouttester', password='secret')
        resp = self.client.get(self.NAV_PAGE)
        self.assertEqual(200, resp.status_code)
        content = resp.content.decode('utf-8')
        logout_url = reverse('logout')

        self.assertNotIn("href=\"{}\"".format(logout_url), content)
        self.assertNotIn("href='{}'".format(logout_url), content)

        soup = BeautifulSoup(content, 'html.parser')
        form = soup.find('form', action=logout_url)
        self.assertIsNotNone(form, "no <form action='{}'> found in the nav".format(logout_url))
        self.assertEqual('post', (form.get('method') or '').lower())
        csrf_input = form.find('input', attrs={'name': 'csrfmiddlewaretoken'})
        self.assertIsNotNone(csrf_input, "logout form is missing {% csrf_token %}")
        self.assertTrue(csrf_input.get('value'))
        submit = form.find('button', attrs={'type': 'submit'}) or form.find('input', attrs={'type': 'submit'})
        self.assertIsNotNone(submit, "logout form has no submit control")


class TestLogoutFormsInErrorTemplates(TestCase):
    """Markup-level regression guard for the two error-page 'log out' links
    (see TestLogoutView's docstring for the incident this is guarding
    against). These templates render inside a <p>, where a nested <form> is
    invalid HTML -- so the fix uses a hidden <form> placed outside the <p>
    plus an inline <button form="..."> instead. These tests render each
    template directly (bypassing the heavier pledge/gift view logic, which
    needs real Transaction/Envelope fixtures unrelated to this fix) and
    assert the button/form wiring is actually correct: matching ids, a real
    POST method, a CSRF token, and the expected 'next' value.
    """

    def setUp(self):
        self.factory = RequestFactory()

    def _rendered(self, template_name, extra_context, path='/some/page/'):
        request = self.factory.get(path)
        request.user = AnonymousUser()
        html = render_to_string(template_name, extra_context, request=request)
        return BeautifulSoup(html, 'html.parser'), path

    def _assert_button_form_wired_correctly(self, soup, button_text, expected_next):
        button = soup.find('button', string=lambda s: s and button_text in s)
        self.assertIsNotNone(button, "no <button> containing {!r}".format(button_text))
        form_id = button.get('form')
        self.assertTrue(form_id, "log out button has no form= attribute")

        form = soup.find('form', id=form_id)
        self.assertIsNotNone(form, "no <form id='{}'> for the log out button".format(form_id))
        self.assertEqual('post', (form.get('method') or '').lower())
        self.assertEqual(reverse('logout'), form.get('action'))

        csrf_input = form.find('input', attrs={'name': 'csrfmiddlewaretoken'})
        self.assertIsNotNone(csrf_input, "log out form is missing {% csrf_token %}")

        next_input = form.find('input', attrs={'name': 'next'})
        self.assertIsNotNone(next_input, "log out form is missing the next= hidden input")
        self.assertEqual(expected_next, next_input.get('value'))

        # The button must live outside the <p> the form-in-<p> HTML bug
        # would have put it in -- confirm it is NOT a descendant of <form>
        # (that would mean we went back to nesting a <form> inside a <p>).
        self.assertIsNone(button.find_parent('form'))

    def test_gift_user_error_logout_form(self):
        soup, path = self._rendered(
            'gift_user_error.html',
            {'envelope': SimpleNamespace(amount=5, cents='00', username='otheruser')},
        )
        self._assert_button_form_wired_correctly(soup, 'log out', expected_next=path)

    def test_pledge_user_error_logout_form(self):
        soup, path = self._rendered(
            'pledge_user_error.html',
            {
                'action': 'pledge',
                'transaction': SimpleNamespace(user=SimpleNamespace(username='otheruser')),
            },
        )
        self._assert_button_form_wired_correctly(soup, 'log out', expected_next=path)


# Sequential-digit dummy string (this codebase's own placeholder convention,
# per ~/.claude/hooks/secret-guard.py) -- used below anywhere a *usable*
# test password is needed. Never a real credential.
_DUMMY_USABLE_PASSWORD = '01234567890123456789'


class TestFindGoogleUsersWithoutPassword(TestCase):
    """Unit tests for find_candidates(), the #1237 pre-removal query.

    Background: #1237 removes the "Sign in with Google" button. A prod
    query (2026-08-31) found 8,457 Google-auth accounts with no usable
    password, all with an email on file -- these tests guard the query
    that finds exactly that population, so nothing ships that email
    (or, later, actually removes the button) blind to who it affects.
    """

    def _make_user(self, username, email='x@example.com', usable_password=True, active=True):
        # password=None makes Django's create_user call set_unusable_password()
        # under the hood -- see django.contrib.auth.base_user.make_password.
        user = User.objects.create_user(
            username=username, email=email,
            password=_DUMMY_USABLE_PASSWORD if usable_password else None,
        )
        if not active:
            user.is_active = False
            user.save()
        return user

    def test_google_user_without_password_is_a_candidate(self):
        user = self._make_user('nopass_google', usable_password=False)
        UserSocialAuth.objects.create(user=user, provider='google-oauth2', uid='g-1')
        self.assertEqual([user], find_candidates())

    def test_legacy_google_provider_is_a_candidate(self):
        # The legacy 'google' provider (2,476 rows on prod, PR #1237
        # comment) -- distinct from the live 'google-oauth2' backend.
        user = self._make_user('legacy_google', usable_password=False)
        UserSocialAuth.objects.create(user=user, provider='google', uid='g-2')
        self.assertEqual([user], find_candidates())

    def test_user_with_usable_password_excluded(self):
        user = self._make_user('haspass_google', usable_password=True)
        UserSocialAuth.objects.create(user=user, provider='google-oauth2', uid='g-3')
        self.assertEqual([], find_candidates())

    def test_user_without_email_excluded(self):
        user = self._make_user('noemail_google', email='', usable_password=False)
        UserSocialAuth.objects.create(user=user, provider='google-oauth2', uid='g-4')
        self.assertEqual([], find_candidates())

    def test_inactive_user_excluded(self):
        user = self._make_user('inactive_google', usable_password=False, active=False)
        UserSocialAuth.objects.create(user=user, provider='google-oauth2', uid='g-5')
        self.assertEqual([], find_candidates())

    def test_user_without_social_auth_excluded(self):
        self._make_user('plain_user', usable_password=False)
        self.assertEqual([], find_candidates())

    def test_provider_filter_restricts_query(self):
        # Once Eric confirms which OAuth client Google actually flagged,
        # --provider lets a rehearsal/run target just that population.
        legacy_user = self._make_user('legacy_only', usable_password=False)
        UserSocialAuth.objects.create(user=legacy_user, provider='google', uid='g-6')
        live_user = self._make_user('live_only', usable_password=False)
        UserSocialAuth.objects.create(user=live_user, provider='google-oauth2', uid='g-7')

        self.assertEqual([legacy_user], find_candidates(providers=('google',)))
        self.assertEqual([live_user], find_candidates(providers=('google-oauth2',)))

    def test_user_with_both_providers_counted_once(self):
        user = self._make_user('both_providers', usable_password=False)
        UserSocialAuth.objects.create(user=user, provider='google-oauth2', uid='g-8a')
        UserSocialAuth.objects.create(user=user, provider='google', uid='g-8b')
        self.assertEqual([user], find_candidates())


class TestEmailGoogleUsersSetPasswordCommand(TestCase):
    """Behavioral tests for the management command itself -- in particular
    the two-key --send / env-var gate described in its module docstring.
    This session (unglueit-0902) never set the env var against a real
    backend; these tests are the only place --send's "actually sends"
    path is exercised, and only against Django's in-memory test backend.
    """

    def _make_candidate(self, username, email):
        user = User.objects.create_user(username=username, email=email, password=None)
        UserSocialAuth.objects.create(user=user, provider='google-oauth2', uid=username)
        return user

    def test_dry_run_sends_nothing(self):
        self._make_candidate('dry1', 'dry1@example.com')
        out = StringIO()
        call_command('email_google_users_set_password', stdout=out)
        self.assertEqual(0, len(mail.outbox))
        self.assertIn('found 1 candidate', out.getvalue())
        self.assertIn('DRY RUN', out.getvalue())

    def test_send_without_env_var_is_a_noop(self):
        self._make_candidate('noenv1', 'noenv1@example.com')
        out = StringIO()
        with mock.patch.dict(os.environ):
            os.environ.pop(SEND_ENV_VAR, None)
            call_command('email_google_users_set_password', '--send', stdout=out)
        self.assertEqual(0, len(mail.outbox))
        self.assertIn(SEND_ENV_VAR, out.getvalue())

    def test_env_var_alone_without_send_flag_is_a_noop(self):
        self._make_candidate('envonly1', 'envonly1@example.com')
        with mock.patch.dict(os.environ, {SEND_ENV_VAR: 'true'}):
            call_command('email_google_users_set_password', stdout=StringIO())
        self.assertEqual(0, len(mail.outbox))

    def test_falsy_env_var_still_blocks_send(self):
        self._make_candidate('falsyenv1', 'falsyenv1@example.com')
        with mock.patch.dict(os.environ, {SEND_ENV_VAR: '0'}):
            call_command('email_google_users_set_password', '--send', stdout=StringIO())
        self.assertEqual(0, len(mail.outbox))

    def test_send_with_env_var_sends_real_email(self):
        user = self._make_candidate('withenv1', 'withenv1@example.com')
        out = StringIO()
        with mock.patch.dict(os.environ, {SEND_ENV_VAR: 'true'}):
            call_command('email_google_users_set_password', '--send', stdout=out)
        self.assertEqual(1, len(mail.outbox))
        sent = mail.outbox[0]
        self.assertEqual([user.email], sent.to)
        self.assertIn('password', sent.subject.lower())
        self.assertIn(user.username, sent.body)
        self.assertIn(reverse('libraryauth_password_reset'), sent.body)

    def test_limit_caps_how_many_are_sent(self):
        for i in range(3):
            self._make_candidate('limituser%d' % i, 'limituser%d@example.com' % i)
        with mock.patch.dict(os.environ, {SEND_ENV_VAR: '1'}):
            call_command(
                'email_google_users_set_password', '--send', '--limit', '2',
                stdout=StringIO(),
            )
        self.assertEqual(2, len(mail.outbox))

    def test_users_with_usable_password_are_never_emailed(self):
        user = User.objects.create_user(
            username='haspass', email='haspass@example.com', password=_DUMMY_USABLE_PASSWORD,
        )
        UserSocialAuth.objects.create(user=user, provider='google-oauth2', uid='haspass')
        with mock.patch.dict(os.environ, {SEND_ENV_VAR: 'true'}):
            call_command('email_google_users_set_password', '--send', stdout=StringIO())
        self.assertEqual(0, len(mail.outbox))

    def test_email_template_is_marked_draft_copy(self):
        # The DRAFT COPY marker lives in a {# ... #} Django comment
        # (deliberately -- it must never render into a real recipient's
        # inbox), so it has to be checked against the template *source*,
        # not the rendered output. Guards against someone dropping the
        # marker before RY has actually rewritten the copy.
        from django.template.loader import get_template
        for template_name in (
            'registration/google_set_password_email.txt',
            'registration/google_set_password_email_subject.txt',
        ):
            source_path = get_template(template_name).origin.name
            with open(source_path, encoding='utf-8') as f:
                self.assertIn('DRAFT COPY', f.read(), template_name)
