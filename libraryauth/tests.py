from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User

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
        resp = self.client.post(reverse('registration_register'),
                                data={'username': 'bob',
                                      'email': 'bob@example.com',
                                      'password1': 'secret',
                                      'password2': 'secret'})
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
        self.assertTrue('Please supply a permanent email address' in resp.content)

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username='badbob')

    def test_is_disposable(self):
        from .emailcheck import is_disposable
        self.assertFalse(is_disposable('eric@hellman.net'))
        self.assertTrue(is_disposable('eric@mailnesia.com'))
