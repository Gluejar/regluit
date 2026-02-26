#external library imports
import re
import mimetypes
from unittest.mock import patch

#django imports
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

#regluit imports
from regluit.core.models import Work, Edition, Ebook, RightsHolder, Claim, Subject

class WishlistTests(TestCase):
    fixtures = ['initial_data.json', 'neuromancer.json']
    def setUp(self):
        self.user = User.objects.create_user('test', 'test@example.org', 'test')
        self.client = Client()
        self.client.login(username='test', password='test')

    def test_add_remove(self):
        # add a book to the wishlist
        r = self.client.post("/wishlist/", {"googlebooks_id": "IDFfMPW32hQC"},
                HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.user.wishlist.works.all().count(), 1)
        wished = self.user.wishlist.works.first()
        # test the work page
        r = self.client.get("/work/%s/" % wished.id)
        self.assertEqual(r.status_code, 200)
        anon_client = Client()
        r = anon_client.get("/work/%s/" % wished.id)
        self.assertEqual(r.status_code, 200)

        # remove the book
        r = self.client.post("/wishlist/", {"remove_work_id": wished.id},
                HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(self.user.wishlist.works.all().count(), 0)

class RhPageTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('test', 'test@example.org', 'test')
        self.rh_user =  User.objects.create_user('rh', 'rh@example.org', 'test')
        self.staff_user =  User.objects.create_superuser('staff', 'staff@example.org', 'test')
        self.work = Work.objects.create(title="test work", language='en')
        rh = RightsHolder.objects.create(rights_holder_name='test', owner=self.rh_user)
        Claim.objects.create(work=self.work, user=self.rh_user, status='active', rights_holder=rh)
        self.kw = Subject.objects.create(name="Fiction")

    def test_anonymous(self):
        anon_client = Client()
        r = anon_client.get("/work/{}/".format(self.work.id))
        r = anon_client.head("/work/{}/".format(self.work.id))
        self.assertEqual(r.status_code, 200)
        csrfmatch =  re.search("name='csrfmiddlewaretoken' value='([^']*)'", str(r.content, 'utf-8'))
        self.assertFalse(csrfmatch)
        r = anon_client.post("/work/{}/kw/".format(self.work.id))
        self.assertEqual(r.status_code, 302)

    def can_edit(self, client, can=True):
        r = client.get("/work/{}/".format(self.work.id))
        self.assertEqual(r.status_code, 200)
        csrfmatch =  re.search("name='csrfmiddlewaretoken' value='([^']*)'", str(r.content, 'utf-8'))
        self.assertTrue(csrfmatch)
        csrf = csrfmatch.group(1)
        r = client.post("/work/{}/kw/".format(self.work.id), {
                'csrfmiddlewaretoken': csrf,
                'kw_add':'true',
                'add_kw_0':'Fiction',
                'add_kw_1':self.kw.id
            })
        if can:
            self.assertEqual(r.content, b'Fiction')
        else:
            self.assertEqual(r.content, b'true')
        r = client.post("/work/{}/kw/".format(self.work.id), {
                'csrfmiddlewaretoken': csrf,
                'remove_kw' : 'Fiction'
            })
        if can:
            self.assertEqual(r.content, b'removed Fiction')
        else:
            self.assertEqual(r.content, b'False')

    def test_user(self):
        # test non-RightsHolder
        client = Client()
        client.login(username='test', password='test')
        self.can_edit(client, can=False)

    def test_rh(self):
        # test RightsHolder
        client = Client()
        client.login(username='rh', password='test')
        self.can_edit(client)

    def test_staff(self):
        client = Client()
        client.login(username='staff', password='test')
        self.can_edit(client)


class PageTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('test', 'test@example.org', 'test')
        User.objects.create_user('test_other', 'test@example.org', 'test_other')
        self.client = Client()
        self.client.login(username='test', password='test')
        w = Work.objects.create(title="test work", language='en')

    def test_setttings(self):
        self.assertEqual(mimetypes.guess_type('/whatever/my_file.epub')[0], 'application/epub+zip')

    def test_view_by_self(self):
        # logged in
        r = self.client.get("/supporter/test/")
        self.assertEqual(r.status_code, 200)
        r = self.client.get("/search/?q=sverige")
        self.assertEqual(r.status_code, 200)
        r = self.client.get("/search/?q=sverige&page=2")
        self.assertEqual(r.status_code, 200)
        r = self.client.get("/notification/settings/")
        self.assertEqual(r.status_code, 200)

    def test_view_by_other(self):
        # someone else's supporter page
        r = self.client.get("/supporter/test_other/")
        self.assertEqual(r.status_code, 200)

    def test_view_by_anonymous(self):
        # not logged in
        anon_client = Client()
        r = anon_client.get("/supporter/test/")
        self.assertEqual(r.status_code, 200)
        r = anon_client.get("/")
        self.assertEqual(r.status_code, 200)
        r = anon_client.get("/search/?q=sverige")
        self.assertEqual(r.status_code, 200)
        r = anon_client.get("/search/?q=sverige&page=2")
        self.assertEqual(r.status_code, 200)
        r = anon_client.get("/info/metrics.html")
        self.assertEqual(r.status_code, 200)
        r = anon_client.get("/marc/")
        self.assertEqual(r.status_code, 200)
        r = anon_client.get("/creativecommons/?order_by=popular")
        self.assertEqual(r.status_code, 200)
        r = anon_client.get("/creativecommons/by")
        self.assertEqual(r.status_code, 200)
        r = anon_client.get("/free/by-nc/?order_by=title")
        self.assertEqual(r.status_code, 200)
        r = anon_client.get("/free/epub/gfdl/")
        self.assertEqual(r.status_code, 200)

class GoogleBooksTest(TestCase):
    fixtures = ['initial_data.json', 'neuromancer.json']
    def test_googlebooks_id(self):
        r = self.client.get("/googlebooks/IDFfMPW32hQC/")
        self.assertEqual(r.status_code, 302)
        work_url = r['location']
        self.assertTrue(re.match(r'.*/work/\d+/$', work_url))


class DownloadProtectionTest(TestCase):
    """
    Tests for PR #1091: bot UA blocking + Cloudflare Turnstile + signed S3 URLs.

    Server-side logic is tested here using mocks for cf.validate() so no real
    Cloudflare network calls are made. See test/playwright_download_protection.py
    for browser-based integration tests against a live server.
    """

    fixtures = ['initial_data.json']

    def setUp(self):
        self.client = Client()
        work = Work.objects.create(title='Test Work', language='en')
        edition = Edition.objects.create(work=work, title='Test Work')
        self.ebook = Ebook.objects.create(
            edition=edition,
            url='https://tieulgnu.s3.amazonaws.com/test/test.epub',
            format='epub',
            rights='https://creativecommons.org/licenses/by/4.0/',
        )
        self.download_url = '/download_ebook/{}/'.format(self.ebook.id)
        self.download_page_url = '/work/{}/download/'.format(work.id)

    # --- Bot UA blocking (Test 5) ---

    def test_known_bot_ua_blocked(self):
        """Known AI crawler UAs should get 403 immediately."""
        bot_uas = [
            'GPTBot/1.0',
            'Mozilla/5.0 (compatible; ClaudeBot/1.0)',
            'Mozilla/5.0 (compatible; PerplexityBot/1.0)',
            'Mozilla/5.0 (compatible; Amazonbot/0.1)',
            'Mozilla/5.0 (compatible; CCBot/2.0)',
        ]
        for ua in bot_uas:
            r = self.client.get(self.download_url, HTTP_USER_AGENT=ua)
            self.assertEqual(r.status_code, 403,
                msg='Expected 403 for bot UA: {}'.format(ua))

    def test_normal_ua_not_hard_blocked(self):
        """Normal browser UAs should not get 403 (Test 6 equivalent)."""
        normal_ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        with patch('regluit.frontend.views.cf.validate', return_value=False):
            r = self.client.get(self.download_url, HTTP_USER_AGENT=normal_ua)
        self.assertNotEqual(r.status_code, 403)

    # --- Turnstile redirect (Tests 2 & 3) ---

    def test_no_token_redirects_to_download_page(self):
        """Direct access with no Turnstile token should redirect to download page (Test 2)."""
        with patch('regluit.frontend.views.cf.validate', return_value=False):
            r = self.client.get(self.download_url)
        self.assertEqual(r.status_code, 302)
        self.assertIn('/download/', r['Location'])

    def test_invalid_token_redirects_to_download_page(self):
        """Fake/invalid token should redirect back to download page (Test 3)."""
        with patch('regluit.frontend.views.cf.validate', return_value=False):
            r = self.client.get(self.download_url + '?cf-turnstile-response=FAKEFAKE')
        self.assertEqual(r.status_code, 302)
        self.assertIn('/download/', r['Location'])

    # --- Valid token → download (Test 4) ---

    def test_valid_token_proceeds_to_download(self):
        """Valid Turnstile token with no EbookFile should redirect to ebook URL."""
        with patch('regluit.frontend.views.cf.validate', return_value=True):
            r = self.client.get(
                self.download_url + '?cf-turnstile-response=VALIDTOKEN'
            )
        self.assertEqual(r.status_code, 302)
        self.assertIn('s3.amazonaws.com', r['Location'])

    def test_valid_token_with_s3_ebookfile_returns_signed_url(self):
        """Valid token with an EbookFile should return a signed S3 URL."""
        from regluit.core.models import EbookFile
        from django.core.files.base import ContentFile
        ebf = EbookFile(ebook=self.ebook, format='epub')
        ebf.file.save('test/test.epub', ContentFile(b'fake epub content'), save=True)
        fake_signed = 'https://tieulgnu.s3.amazonaws.com/test/test.epub?X-Amz-Signature=abc'
        with patch('regluit.frontend.views.cf.validate', return_value=True), \
             patch('regluit.frontend.views._generate_signed_s3_url', return_value=fake_signed):
            r = self.client.get(
                self.download_url + '?cf-turnstile-response=VALIDTOKEN'
            )
        self.assertEqual(r.status_code, 302)
        self.assertIn('X-Amz-Signature', r['Location'])


