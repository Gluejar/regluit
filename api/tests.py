import json
import datetime
from decimal import Decimal

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from regluit.core import bookloader, models

class ApiTests(TestCase):

    def setUp(self):
        edition = bookloader.add_by_isbn(isbn='0441012035')
        campaign = models.Campaign.objects.create(
            name=edition.work.title,
            work=edition.work, 
            description='Test Campaign',
            deadline=datetime.datetime.now(),
            target=Decimal('1000.00'),
        )
        self.user = User.objects.create_user('test', 'test@example.com', 'testpass')
        self.client = Client()

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
        self.assertEqual(j['objects'][0]['work'], '/api/v1/work/1/')

    def test_campaign(self):
        r = self.client.get('/api/v1/campaign/1/', data={
            'format': 'json', 
            'username': self.user.username, 
            'api_key': self.user.api_key.key
        })
        self.assertEqual(r.status_code, 200)
        j = json.loads(r.content)
        self.assertEqual(j['name'], 'Neuromancer')
        self.assertEqual(j['work'], '/api/v1/work/1/')

    def test_campaign_lookup_by_isbn(self):
        r = self.client.get('/api/v1/campaign/', data={
            'format': 'json', 
            'work__editions__isbn_10': '0441012035', 
            'username': self.user.username, 
            'api_key': self.user.api_key.key
        })
        self.assertEqual(r.status_code, 200)
        j = json.loads(r.content)
        self.assertEqual(len(j['objects']), 1)
        self.assertEqual(j['objects'][0]['name'], 'Neuromancer')
        self.assertEqual(j['meta']['logged_in_username'], None)
        self.assertEqual(j['objects'][0]['in_wishlist'], False)

    def test_logged_in_user_info(self):
        # login and see if adding a work to the users wishlist causes
        # it to show up as in_wishlist in the campaign info
        self.client.login(username='test', password='testpass')

        r = self.client.get('/api/v1/campaign/', data={
            'format': 'json', 
            'work__editions__isbn_10': '0441012035', 
            'username': self.user.username, 
            'api_key': self.user.api_key.key
        })
        j = json.loads(r.content)
        self.assertEqual(j['meta']['logged_in_username'], 'test')
        self.assertEqual(j['objects'][0]['in_wishlist'], False)

        w = models.Work.objects.get(editions__isbn_10='0441012035') 
        self.user.wishlist.add_work(w,'test')
        r = self.client.get('/api/v1/campaign/', data={
            'format': 'json', 
            'work__editions__isbn_10': '0441012035', 
            'username': self.user.username, 
            'api_key': self.user.api_key.key
        })
        j = json.loads(r.content)
        self.assertEqual(j['meta']['logged_in_username'], 'test')
        self.assertEqual(j['objects'][0]['in_wishlist'], True)

