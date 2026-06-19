from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.cache import cache


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
        for _key, ref in user_activated.receivers:
            fn = ref if getattr(ref, '__name__', None) else (ref() if callable(ref) else None)
            names.append(getattr(fn, '__name__', None))
        self.assertIn('handle_same_email_account', names)
