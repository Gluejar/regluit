"""
external library imports
"""
import json
from decimal import Decimal

"""
django imports
"""
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from django.utils.timezone import now

"""
regluit imports
"""
import regluit.core.isbn

from regluit.core import models
from regluit.api import models as apimodels

class ApiTests(TestCase):
    fixtures = ['initial_data.json', 'neuromancer.json']
    work_id=None

    def setUp(self):
        edition = models.Edition.objects.get(pk=1)
        self.work_id=edition.work_id
        campaign = models.Campaign.objects.create(
            name=edition.work.title,
            work=edition.work,
            description='Test Campaign',
            deadline=now(),
            target=Decimal('1000.00'),
        )
        self.user = User.objects.create_user('test', 'test@example.org', 'testpass')
        self.client = Client()
        ebook = models.Ebook.objects.create(
            url="http://example.com/ebook",
            provider="github",
            rights='CC BY',
            format='epub',
            edition=edition,
        )

    def test_widget(self):
        r = self.client.get('/api/widget/0441007465/')
        self.assertEqual(r.status_code, 200)
        r = self.client.get('/api/widget/%s/'%self.work_id)
        self.assertEqual(r.status_code, 200)

    def test_widget_unknown_ids_return_empty_widget(self):
        # Regression for #1156: bad identifiers must render an empty widget (200),
        # not raise an uncaught exception (500).
        # non-numeric token (length != 10/13) -> safe_get_work raises Work.DoesNotExist
        r = self.client.get('/api/widget/featured4iL7gEXx/')
        self.assertEqual(r.status_code, 200)
        # numeric but no such work
        r = self.client.get('/api/widget/999999999/')
        self.assertEqual(r.status_code, 200)
        # invalid ISBN-10 -> convert_10_to_13 returns None (was len(None) TypeError)
        r = self.client.get('/api/widget/ABCDEFGHIJ/')
        self.assertEqual(r.status_code, 200)

class FeedTests(TestCase):
    fixtures = ['initial_data.json', 'neuromancer.json']
    def setUp(self):
        edition = models.Edition.objects.get(pk=1)
        ebook = models.Ebook.objects.create(edition=edition, url='http://example.org/', format='epub', rights='CC BY')
        self.test_work_id = edition.work_id

    def test_opds(self):
        r = self.client.get('/api/opds/creative_commons/')
        self.assertEqual(r.status_code, 200)
        r = self.client.get('/api/opds/epub/?order_by=featured')
        self.assertEqual(r.status_code, 200)
        r = self.client.get('/api/opds/by/pdf/?order_by=popular')
        self.assertEqual(r.status_code, 200)
        r = self.client.get('/api/opds/active_campaigns/?order_by=title')
        self.assertEqual(r.status_code, 200)
        r = self.client.get('/api/opds/?work=%s' % self.test_work_id)
        self.assertEqual(r.status_code, 200)

    def test_opds_all_keyword_alias_works(self):
        r = self.client.get('/api/opds/all/kw.Fiction/')
        self.assertEqual(r.status_code, 200)

    def test_opds_keyword_compound_returns_404(self):
        r = self.client.get('/api/opds/kw.Fiction/epub/')
        self.assertEqual(r.status_code, 404)

    def test_opds_single_keyword_works(self):
        r = self.client.get('/api/opds/kw.Fiction/')
        self.assertEqual(r.status_code, 200)

    def test_opdsjson_keyword_compound_returns_404(self):
        r = self.client.get('/api/opdsjson/kw.Fiction/epub/')
        self.assertEqual(r.status_code, 404)

    def test_onix_keyword_compound_returns_404(self):
        r = self.client.get('/api/onix/kw.Fiction/epub/')
        self.assertEqual(r.status_code, 404)


    def test_nix(self):
        r = self.client.get('/api/onix/by/')
        self.assertEqual(r.status_code, 200)
        r = self.client.get('/api/onix/cc0/')
        self.assertEqual(r.status_code, 200)
        r = self.client.get('/api/onix/epub/?max=10')
        self.assertEqual(r.status_code, 200)
        r = self.client.get('/api/onix/?work=%s' % self.test_work_id)
        self.assertEqual(r.status_code, 200)

    def test_onix_all_keyword_alias_works(self):
        r = self.client.get('/api/onix/all/kw.Fiction/')
        self.assertEqual(r.status_code, 200)

class AllowedRepoTests(TestCase):
    def setUp(self):
        apimodels.AllowedRepo.objects.create(org='test',repo_name='test')
        apimodels.AllowedRepo.objects.create(org='star',repo_name='*')

    def test_urls(self):
        #good
        self.assertTrue(apimodels.repo_allowed('https://github.com/test/test/raw/master/metadata.yaml')[0])
        self.assertTrue(apimodels.repo_allowed('https://github.com/star/test/raw/master/metadata.yaml')[0])
        # bad urls
        self.assertFalse(apimodels.repo_allowed('auhf8peargp8ge')[0])
        self.assertFalse(apimodels.repo_allowed('')[0])
        self.assertFalse(apimodels.repo_allowed('http://github.com/test/test/raw/master/metadata.yaml')[0])
        self.assertFalse(apimodels.repo_allowed('https://github.com/test/test/raw/master/samples/metadata.yaml')[0])
        self.assertFalse(apimodels.repo_allowed('https://github.com/test/test/raw/branch/metadata.yaml')[0])
        self.assertFalse(apimodels.repo_allowed('https://github.com/test/test/master/metadata.yaml')[0])
        self.assertFalse(apimodels.repo_allowed('https://github.com/test/test/raw/master/metadata.json')[0])

class WebHookTests(TestCase):
    fixtures = ['initial_data.json']
    def test_travisci_webhook(self):
        """
        test of api.views.travisci_webhook
        """

        payload = json.dumps({
          "repository":{
              "id":4651401,
              "name":"Adventures-of-Huckleberry-Finn_76",
              "owner_name":"GITenberg",
              "url":"http://GITenberg.github.com/"
           },
          "status_message": "Passed",
          "type": "push"
        })

        invalid_payload = json.dumps({
          "repository":{
              "id":4651401,
              "name":"",
              "url":"http://GITenberg.github.com/"
           },
          "status_message": "Passed",
          "type": "push"
        })

        url = "/api/travisci/webhook"

        # 200 if a simple get
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

        # 200 when we actually load a valid repo (should we use 201?)
        r = self.client.post(url, data={'payload':payload}, headers={}, allow_redirects=True)
        self.assertEqual(r.status_code, 200)

        # 400 error if we get exception when trying to load a book
        r = self.client.post(url, data={'payload':invalid_payload}, headers={}, allow_redirects=True)
        self.assertEqual(r.status_code, 400)
