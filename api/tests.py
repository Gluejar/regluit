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

    def test_user(self):
        self.assertEqual(User.objects.all().count(), 1)
        self.assertTrue(User.objects.all()[0].api_key.key)

    def test_no_auth(self):
        r = self.client.get('/api/v1/campaign/', data={'format': 'json'})
        self.assertEqual(r.status_code, 401)

    def test_campaigns(self):
        r = self.client.get('/api/v1/campaign/', data={
            'format': 'json', 
            'username': self.user.username, 
            'api_key': self.user.api_key.key
        })
        self.assertEqual(r.status_code, 200)
        j = json.loads(r.content)
        self.assertEqual(len(j['objects']), 1)
        self.assertEqual(j['objects'][0]['name'], 'Neuromancer')
        self.assertEqual(j['objects'][0]['work'], '/api/v1/work/%s/' % self.work_id)
        resource_uri=j['objects'][0]['resource_uri']
        r = self.client.get( resource_uri, data={
            'format': 'json', 
            'username': self.user.username, 
            'api_key': self.user.api_key.key
        })
        self.assertEqual(r.status_code, 200)
        j = json.loads(r.content)
        self.assertEqual(j['name'], 'Neuromancer')
        self.assertEqual(j['work'], '/api/v1/work/%s/' % self.work_id)

    def test_campaign_lookup_by_isbn(self):
        r = self.client.get('/api/v1/campaign/', data={
            'format': 'json', 
            'work__identifiers__value': regluit.core.isbn.convert_10_to_13('0441007465'), 
            'work__identifiers__type': 'isbn', 
            'username': self.user.username, 
            'api_key': self.user.api_key.key
        })
        self.assertEqual(r.status_code, 200)
        j = json.loads(r.content)
        self.assertEqual(len(j['objects']), 1)
        self.assertEqual(j['objects'][0]['name'], 'Neuromancer')
        self.assertEqual(j['meta']['logged_in_username'], None)
        self.assertEqual(j['objects'][0]['in_wishlist'], False)

    def test_identifier_lookup(self):
        r = self.client.get('/api/v1/identifier/', data={
            'format': 'json', 
            'value': regluit.core.isbn.convert_10_to_13('0441007465'), 
            'type': 'isbn', 
            'username': self.user.username, 
            'api_key': self.user.api_key.key
        })
        self.assertEqual(r.status_code, 200)

    def test_logged_in_user_info(self):
        # login and see if adding a work to the users wishlist causes
        # it to show up as in_wishlist in the campaign info
        self.client.login(username='test', password='testpass')

        r = self.client.get('/api/v1/campaign/', data={
            'format': 'json', 
            'work__identifiers__value': regluit.core.isbn.convert_10_to_13('0441007465'), 
            'work__identifiers__type': 'isbn', 
            'username': self.user.username, 
            'api_key': self.user.api_key.key
        })
        j = json.loads(r.content)
        self.assertEqual(j['meta']['logged_in_username'], 'test')
        self.assertEqual(j['objects'][0]['in_wishlist'], False)

        w = models.Work.objects.get(identifiers__value=regluit.core.isbn.convert_10_to_13('0441007465'), identifiers__type='isbn') 
        self.user.wishlist.add_work(w,'test')
        r = self.client.get('/api/v1/campaign/', data={
            'format': 'json', 
            'work__identifiers__value': regluit.core.isbn.convert_10_to_13('0441007465'), 
            'work__identifiers__type': 'isbn', 
            'username': self.user.username, 
            'api_key': self.user.api_key.key
        })
        j = json.loads(r.content)
        self.assertEqual(j['meta']['logged_in_username'], 'test')
        self.assertEqual(j['objects'][0]['in_wishlist'], True)

        r = self.client.get('/api/v1/free/', data={
            'format': 'json', 
            'isbn': '0441007465', 
            'username': self.user.username, 
            'api_key': self.user.api_key.key
        })
        j = json.loads(r.content)
        self.assertEqual(j['objects'][0]['filetype'], 'epub')
        r = self.client.get('/api/v1/free/', data={
            'format': 'xml', 
            'isbn': '0441007465', 
            'username': self.user.username, 
            'api_key': self.user.api_key.key
        })
        self.assertTrue(r.content.find('<rights>CC BY</rights>')>0)

    def test_widget(self):
        r = self.client.get('/api/widget/0441007465/')
        self.assertEqual(r.status_code, 200)
        r = self.client.get('/api/widget/%s/'%self.work_id)
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

    def test_nix(self):
        r = self.client.get('/api/onix/by/')
        self.assertEqual(r.status_code, 200)
        r = self.client.get('/api/onix/cc0/')
        self.assertEqual(r.status_code, 200)
        r = self.client.get('/api/onix/epub/?max=10')
        self.assertEqual(r.status_code, 200)
        r = self.client.get('/api/onix/?work=%s' % self.test_work_id)
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
        
        
