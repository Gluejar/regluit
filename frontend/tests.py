import re

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from regluit.core.models import Work, Campaign

from decimal import Decimal as D
import datetime

class WishlistTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('test', 'test@example.org', 'test')
        self.client = Client()
        self.client.login(username='test', password='test')

    def test_add_remove(self):
        # add a book to the wishlist
        r = self.client.post("/wishlist/", {"googlebooks_id": "2NyiPwAACAAJ"}, 
                HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(r.status_code, 302)
        self.assertEqual(self.user.wishlist.works.all().count(), 1)

        # test the work page
        r = self.client.get("/work/1/")
        self.assertEqual(r.status_code, 200)
        anon_client = Client()
        r = anon_client.get("/work/1/")
        self.assertEqual(r.status_code, 200)

        # remove the book
        r = self.client.post("/wishlist/", {"remove_work_id": "1"}, 
                HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(self.user.wishlist.works.all().count(), 0)

class PageTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('test', 'test@example.org', 'test')
        self.user = User.objects.create_user('test_other', 'test@example.org', 'test_other')
        self.client = Client()
        self.client.login(username='test', password='test')

    def test_view_by_self(self):
        # logged in
        r = self.client.get("/supporter/test/")
        self.assertEqual(r.status_code, 200)
        r = self.client.get("/search/?q=sverige")
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

class GoogleBooksTest(TestCase):

    def test_googlebooks_id(self):
        r = self.client.get("/googlebooks/wtPxGztYx-UC/")
        self.assertEqual(r.status_code, 302)
        work_url = r['location']
        self.assertTrue(re.match('.*/work/\d+/$', work_url))

        r = self.client.get("/googlebooks/wtPxGztYx-UC/")
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r['location'], work_url)

class CampaignUiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'test@example.org', 'test')
        self.client = Client()
        # load a Work and a Campaign to create a Pledge page
        self.work = Work(title="test Work")
        self.work.save()
        self.campaign = Campaign(target=D('1000.00'), deadline=datetime.datetime.utcnow() + datetime.timedelta(days=180),
                                 work=self.work)
        self.campaign.save()
        self.campaign.activate()

    def test_login_required_for_pledge(self):
        """ Make sure that the user has to be logged in to be able to access a pledge page"""
        pledge_path = reverse("pledge", kwargs={'work_id': self.work.id})
        r = self.client.get(pledge_path)
        self.assertEqual(r.status_code, 302)
        
        # now login and see whether the pledge page is accessible
        self.client.login(username='test', password='test')
        r = self.client.get(pledge_path)
        self.assertEqual(r.status_code, 200)
        
    def tearDown(self):
        pass