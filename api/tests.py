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

"""
regluit imports
"""
import regluit.core.isbn

from regluit.core import bookloader, models
from regluit.utils.localdatetime import now

class ApiTests(TestCase):
    work_id=None
    
    def setUp(self):
        edition = bookloader.add_by_isbn_from_google(isbn='0441007465')
        self.work_id=edition.work.id
        campaign = models.Campaign.objects.create(
            name=edition.work.title,
            work=edition.work, 
            description='Test Campaign',
            deadline=now(),
            target=Decimal('1000.00'),
        )
        self.user = User.objects.create_user('test', 'test@example.org', 'testpass')
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

