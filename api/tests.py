import json
import datetime

from django.test import TestCase
from django.test.client import Client

from regluit.core import bookloader, models

class CampaignTests(TestCase):

    def setUp(self):
        edition = bookloader.add_book(isbn='0441012035')
        campaign = models.Campaign.objects.create(
            name=edition.work.title,
            work=edition.work, 
            description='Test Campaign',
            deadline=datetime.datetime.now(),
            target=1000.0,
        )
        self.client = Client()

    def test_campaigns(self):
        r = self.client.get('/api/v1/campaign/', data={'format': 'json'})
        self.assertEqual(r.status_code, 200)
        j = json.loads(r.content)
        self.assertEqual(len(j['objects']), 1)
        self.assertEqual(j['objects'][0]['name'], 'Neuromancer')
        self.assertEqual(j['objects'][0]['work'], '/api/v1/work/1/')

    def test_campaign(self):
        r = self.client.get('/api/v1/campaign/1/', data={'format': 'json'})
        self.assertEqual(r.status_code, 200)
        j = json.loads(r.content)
        self.assertEqual(j['name'], 'Neuromancer')
        self.assertEqual(j['work'], '/api/v1/work/1/')

    def test_campaign_lookup_by_isbn(self):
        url = '/api/v1/campaign/?work__editions__isbn_10=0441012035'
        r = self.client.get('/api/v1/campaign/', data={'format': 'json', 'work__editions__isbn_10': '0441012035'})
        self.assertEqual(r.status_code, 200)
        j = json.loads(r.content)
        self.assertEqual(len(j['objects']), 1)
        self.assertEqual(j['objects'][0]['name'], 'Neuromancer')
