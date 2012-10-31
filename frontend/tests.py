import re

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings

from regluit.core.models import Work, Campaign, RightsHolder, Claim

from decimal import Decimal as D
from regluit.utils.localdatetime import now
from datetime import timedelta

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
        wished= self.user.wishlist.works.all()[0]
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
        r = anon_client.get("/info/metrics.html")
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
        self.campaign = Campaign(target=D('1000.00'), deadline=now() + timedelta(days=180),
                                 work=self.work)
        self.campaign.save()

        rh = RightsHolder(owner = self.user, rights_holder_name = 'rights holder name')
        rh.save()
        cl = Claim(rights_holder = rh, work = self.work, user = self.user, status = 'active')
        cl.save()

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
    
class PledgingUiTests(TestCase):
    def setUp(self):
        self.USERNAME = 'testname'
        self.PASSWORD = 'testpw'
        self.EMAIL = 'test@example.org'
        self.user = User.objects.create_user(self.USERNAME, self.EMAIL, self.PASSWORD)
        self.client = Client()
        
        # login and heck whether user logged in
        self.assertTrue(self.client.login(username=self.USERNAME, password=self.PASSWORD))
        # http://stackoverflow.com/a/6013115
        self.assertEqual(self.client.session['_auth_user_id'], self.user.pk)        
        
        # load a Work by putting it on the User's wishlist
        r = self.client.post("/wishlist/", {"googlebooks_id": "2NyiPwAACAAJ"}, 
                HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(r.status_code, 302)
        self.assertEqual(self.user.wishlist.works.all().count(), 1)
        wished= self.user.wishlist.works.all()[0]
        # test the work page
        r = self.client.get("/work/%s/" % wished.id)
        self.assertEqual(r.status_code, 200)
        anon_client = Client()
        r = anon_client.get("/work/%s/" % wished.id)
        self.assertEqual(r.status_code, 200)        
        
        # load a Work and a Campaign to create a Pledge page
        self.work = self.user.wishlist.works.all()[0]
        self.campaign = Campaign(target=D('1000.00'), deadline=now() + timedelta(days=180),
                                 work=self.work)
        self.campaign.save()

        rh = RightsHolder(owner = self.user, rights_holder_name = 'rights holder name')
        rh.save()
        cl = Claim(rights_holder = rh, work = self.work, user = self.user, status = 'active')
        cl.save()

        self.campaign.activate()        

        
    def test_successful_stripe_pledge(self):
        """can we land on the work page and submit a stripe token?"""
        # work page and hit support
        
        r = self.client.get("/work/%s/" % self.work.id)
        self.assertEqual(r.status_code, 200)

        # go to pledge page
        r = self.client.get("/pledge/%s" % self.work.id, data={}, follow=True)
        self.assertEqual(r.status_code, 200)
        
        # submit to pledge page
        r = self.client.post("/pledge/%s" % self.work.id, data={'preapproval_amount':'10',
                                                                'premium_id':'150'}, follow=True)
        self.assertEqual(r.status_code, 200)        
        
        
    def tearDown(self):
        pass

class UnifiedCampaignTests(TestCase):
    fixtures=['basic_campaign_test.json']
    def test_setup(self):
        # testing basics:  are there 3 users?
        from django.contrib.auth.models import User
        self.assertEqual(User.objects.count(), 3)
        # make sure we know the passwords for the users
        #RaymondYee / raymond.yee@gmail.com / Test_Password_
        #hmelville / rdhyee@yahoo.com / gofish!
        #dataunbound / raymond.yee@dataunbound.com / numbers_unbound
        self.client = Client()
        self.assertTrue(self.client.login(username="RaymondYee", password="Test_Password_"))
        self.assertTrue(self.client.login(username="hmelville", password="gofish!"))
        self.assertTrue(self.client.login(username="dataunbound", password="numbers_unbound"))

        
    def test_relaunch(self):
        # how much of test.campaigntest.test_relaunch can be done here?
        pass
    
