from types import SimpleNamespace

from bs4 import BeautifulSoup
from django.conf import settings
from django.urls import reverse
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.core.cache import cache
from django.template.loader import render_to_string


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


class TestGoogleLoginRemoved(TestCase):
    """Regression guard for the Google-login removal (2026-08-30).

    Eric asked to remove the "Sign in with Google" button (Gmail thread
    1a04cd3f47fac2a2) after Google flagged unglue.it's OAuth client
    (569579163337-...) as inactive >=5 months and due for deletion ~Sept 25,
    2026. Removed: the Google backend from AUTHENTICATION_BACKENDS and every
    "Sign in/Sign Up with Google" link (login, home, gift_login,
    from_pledge, registration_form). Left in place on purpose: social_django
    itself, the generic social-auth pipeline, and OpenIdAuth -- so existing
    Google-linked users' UserSocialAuth rows stay intact and queryable, and
    a still-registered (if unused) backend keeps working. These tests would
    have caught a page still advertising a login option whose backend is
    gone.
    """
    fixtures = ['initial_data.json']

    def setUp(self):
        # Pre-existing, unrelated flake: templatetags/puzzle.py reads
        # `cache.get('encode_answers')` once at *import* time rather than
        # per-request, and only libraryauth/forms.py ever populates that
        # cache key. If this test class is the first thing in a test run to
        # touch a `{% puzz %}` template (home.html, registration_form.html)
        # before something has imported forms.py, puzzle.encode_answers is
        # still None and any such page render raises TypeError -- reproduces
        # identically on unmodified master, nothing to do with Google login.
        # Import forms.py here (its own module-level code populates the
        # cache) and patch puzzle's already-cached reference if it grabbed
        # None before that happened.
        from . import forms as _forms  # noqa: F401 (import side effect only)
        from .templatetags import puzzle as _puzzle
        if _puzzle.encode_answers is None:
            _puzzle.encode_answers = _forms.encoder

    def _assert_no_google_markup(self, content):
        self.assertNotIn('google-oauth2', content)
        self.assertNotIn('btn-google-plus', content)
        self.assertNotIn('Sign in with Google', content)
        self.assertNotIn('Sign Up with Google', content)

    def _assert_no_google_button(self, path):
        resp = self.client.get(path)
        self.assertEqual(200, resp.status_code)
        self._assert_no_google_markup(resp.content.decode('utf-8'))

    def test_login_page_has_no_google_button(self):
        self._assert_no_google_button(reverse('superlogin'))

    def test_home_page_has_no_google_button(self):
        # Not a full render: home() requires a featured Campaign these
        # fixtures don't provide (a pre-existing fixture gap unrelated to
        # this change -- reproduces identically on unmodified master), and
        # the template itself pulls in unrelated live data (campaigns,
        # books) that would need to be faked just to reach the signup box.
        # Reading the template source directly is weaker than a live
        # render but fully deterministic, and still catches the actual
        # regression this guards against: the button's markup returning.
        from django.template.loader import get_template
        source_path = get_template('home.html').origin.name
        with open(source_path, encoding='utf-8') as f:
            self._assert_no_google_markup(f.read())

    def test_registration_page_has_no_google_button(self):
        self._assert_no_google_button(reverse('registration_register'))

    def test_google_backend_not_registered(self):
        self.assertNotIn(
            'social_core.backends.google.GoogleOAuth2',
            settings.AUTHENTICATION_BACKENDS,
        )

    def test_openid_backend_still_registered(self):
        # Confirms the removal was scoped to Google, not social_django as a
        # whole -- OpenIdAuth (unused elsewhere, but not this change's job
        # to touch) must still be there.
        self.assertIn(
            'social_core.backends.open_id.OpenIdAuth',
            settings.AUTHENTICATION_BACKENDS,
        )

    def test_google_oauth_begin_url_no_longer_reaches_google(self):
        # With the backend deregistered, python-social-auth must refuse the
        # begin URL rather than redirect to accounts.google.com -- otherwise
        # a stale bookmark/crawled link would still complete a login.
        resp = self.client.get('/socialauth/login/google-oauth2/', follow=False)
        self.assertNotEqual(302, resp.status_code)
        if resp.status_code == 302:
            self.assertNotIn('accounts.google.com', resp['Location'])
