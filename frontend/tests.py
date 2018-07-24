#external library imports
import json
import re
import mimetypes

from datetime import timedelta
from decimal import Decimal as D

#django imports
from django.contrib import auth
from django.contrib.auth.models import User
from django.core import mail
from django.urls import reverse
from django.test import TestCase
from django.test.client import Client
from django.utils.timezone import now

from notification.models import Notice

#regluit imports
from regluit.core.models import Work, Campaign, RightsHolder, Claim, Subject
from regluit.payment.models import Transaction
from regluit.payment.manager import PaymentManager
from regluit.payment.stripelib import StripeClient, TEST_CARDS, ERROR_TESTING, card

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
        wished = self.user.wishlist.works.all()[0]
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
        csrfmatch =  re.search("name='csrfmiddlewaretoken' value='([^']*)'", r.content)
        self.assertFalse(csrfmatch)
        r = anon_client.post("/work/{}/kw/".format(self.work.id))
        self.assertEqual(r.status_code, 302)

    def can_edit(self, client, can=True):
        r = client.get("/work/{}/".format(self.work.id))
        self.assertEqual(r.status_code, 200)
        csrfmatch =  re.search("name='csrfmiddlewaretoken' value='([^']*)'", r.content)
        self.assertTrue(csrfmatch)
        csrf = csrfmatch.group(1)
        r = client.post("/work/{}/kw/".format(self.work.id), {
                u'csrfmiddlewaretoken': csrf,
                u'kw_add':u'true',
                u'add_kw_0':u'Fiction',
                u'add_kw_1':self.kw.id
            })
        if can:
            self.assertEqual(r.content, u'Fiction')
        else:
            self.assertEqual(r.content, u'true')
        r = client.post("/work/{}/kw/".format(self.work.id), {
                u'csrfmiddlewaretoken': csrf,
                u'remove_kw' : u'Fiction'
            })
        if can:
            self.assertEqual(r.content, u'removed Fiction')
        else:
            self.assertEqual(r.content, u'False')

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

class CampaignUiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'test@example.org', 'test')
        self.client = Client()
        # load a Work and a Campaign to create a Pledge page
        self.work = Work(title="test Work")
        self.work.save()
        self.campaign = Campaign(target=D('1000.00'), deadline=now() + timedelta(days=180),
                                 work=self.work, description='dummy description')
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
    fixtures = ['initial_data.json', 'neuromancer.json']
    def setUp(self):
        self.USERNAME = 'testname'
        self.PASSWORD = 'testpw'
        self.EMAIL = 'test@example.org'
        self.user = User.objects.create_user(self.USERNAME, self.EMAIL, self.PASSWORD)
        self.client = Client()

        # login and heck whether user logged in
        self.assertTrue(self.client.login(username=self.USERNAME, password=self.PASSWORD))
        # https://stackoverflow.com/a/6013115
        #self.assertEqual(self.client.session['_auth_user_id'], self.user.pk)  
        
        user = auth.get_user(self.client)
        assert user.is_authenticated


        # load a Work by putting it on the User's wishlist
        r = self.client.post("/wishlist/", {"googlebooks_id": "IDFfMPW32hQC"},
                HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.user.wishlist.works.all().count(), 1)
        wished = self.user.wishlist.works.all()[0]
        # test the work page
        r = self.client.get("/work/%s/" % wished.id)
        self.assertEqual(r.status_code, 200)
        anon_client = Client()
        r = anon_client.get("/work/%s/" % wished.id)
        self.assertEqual(r.status_code, 200)

        # load a Work and a Campaign to create a Pledge page
        self.work = self.user.wishlist.works.all()[0]
        self.campaign = Campaign(target=D('1000.00'), deadline=now() + timedelta(days=180),
                                 work=self.work, description='dummy description')
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
    fixtures = ['initial_data.json','basic_campaign_test.json']

    def verify_setup(self):
        # testing basics:  are there 3 users?

        self.assertEqual(User.objects.count(), 3)
        # make sure we know the passwords for the users
        #RaymondYee / raymond.yee@gmail.com / Test_Password_
        #hmelville / rdhyee@yahoo.com / gofish!
        #dataunbound / raymond.yee@dataunbound.com / numbers_unbound
        self.client = Client()
        self.assertTrue(self.client.login(username="RaymondYee", password="Test_Password_"))
        self.assertTrue(self.client.login(username="hmelville", password="gofish!"))
        self.assertTrue(self.client.login(username="dataunbound", password="numbers_unbound"))

        # how many works and campaigns?
        self.assertEqual(Work.objects.count(), 3)
        self.assertEqual(Campaign.objects.count(), 2)

    def do_test_junk_webhook(self):
        """send in junk json and then an event that doesn't exist"""
        # non-json
        ipn_url = reverse("HandleIPN", args=('stripelib',))
        r = self.client.post(ipn_url, data="X", content_type="application/json; charset=utf-8")
        self.assertEqual(r.status_code, 400)
        # junk event_id
        r = self.client.post(ipn_url, data='{"id": "evt_XXXXXXXXX"}', content_type="application/json; charset=utf-8")
        self.assertEqual(r.status_code, 400)

    def pledge_to_work_with_cc(self, username, password, work_id, card, preapproval_amount='10', premium_id='150'):

        # how much of test.campaigntest.test_relaunch can be done here?
        self.assertTrue(self.client.login(username=username, password=password))

        # Pro Web 2.0 Mashups
        self.work = Work.objects.get(id=work_id)
        r = self.client.get("/work/%s/" % (self.work.id))

        r = self.client.get("/work/%s/" % self.work.id)
        self.assertEqual(r.status_code, 200)

        # go to pledge page
        r = self.client.get("/pledge/%s" % self.work.id, data={}, follow=True)
        self.assertEqual(r.status_code, 200)

        # submit to pledge page
        r = self.client.post("/pledge/%s/" % self.work.id, data={'preapproval_amount': preapproval_amount,
                                                                'premium_id':premium_id}, follow=True)
        self.assertEqual(r.status_code, 200)

        # Should now be on the fund page
        pledge_fund_path = r.request.get('PATH_INFO')
        self.assertTrue(pledge_fund_path.startswith('/payment/fund'))
        # pull out the transaction info
        t_id = int(pledge_fund_path.replace('/payment/fund/',''))

        # r.content holds the page content
        # create a stripe token to submit to form


        sc = StripeClient()
        stripe_token = sc.create_token(card=card)

        # track start time and end time of these stipe interactions so that we can limit the window of Events to look for
        # time0 = time.time() <--- this method was brittle because of clock skew and latency
        time0 = stripe_token['created']
        r = self.client.post(pledge_fund_path, data={'stripe_token':stripe_token.id}, follow=True)

        # where are we now?
        self.assertEqual(r.request.get('PATH_INFO'), '/fund/complete/')
        self.assertEqual(r.status_code, 200)

        # dig up the transaction and charge it
        pm = PaymentManager()
        transaction = Transaction.objects.get(id=t_id)

        # catch any exception and pass it along
        try:
            self.assertTrue(pm.execute_transaction(transaction, ()))
        except Exception, charge_exception:
            pass
        else:
            charge_exception = None

        # retrieve events from this period
        events = list(sc._all_objs('Event', created={'gte': time0}))

        return (events, charge_exception)

    def good_cc_scenario(self):
        # how much of test.campaigntest.test_relaunch can be done here?

        card1 = card(number=TEST_CARDS[0][0], exp_month=1, exp_year='2020', cvc='123', name='Raymond Yee',
          address_line1="100 Jackson St.", address_line2="", address_zip="94706", address_state="CA", address_country=None)  # good card

        (events, charge_exception) = self.pledge_to_work_with_cc(username="RaymondYee", password="Test_Password_", work_id=1, card=card1,
                               preapproval_amount='10', premium_id='150')

        self.assertEqual(charge_exception, None)

        # expect to have 3 events (there is a possibility that someone else could be running tests on this stripe account at the same time)
        # events returned sorted in reverse chronological order.

        self.assertEqual(len(events), 3)
        self.assertEqual(events[0].type, 'charge.succeeded')
        self.assertEqual(events[1].type, 'customer.card.created')
        self.assertEqual(events[2].type, 'customer.created')

        # now feed each of the events to the IPN processor.
        ipn_url = reverse("HandleIPN", args=('stripelib',))

        for (i, event) in enumerate(events):
            r = self.client.post(ipn_url, data=json.dumps({"id": event.id}), content_type="application/json; charset=utf-8")
            self.assertEqual(r.status_code, 200)

        # expected notices

        self.assertEqual(len(Notice.objects.filter(notice_type__label='pledge_you_have_pledged', recipient__username='RaymondYee')), 1)
        self.assertEqual(len(Notice.objects.filter(notice_type__label='pledge_charged', recipient__username='RaymondYee')), 1)


    def bad_cc_scenario(self):
        """Goal of this scenario: enter a CC that will cause a charge.failed event, have user repledge succesfully"""

        card1 = card(number=ERROR_TESTING['BAD_ATTACHED_CARD'][0])

        (events, charge_exception) = self.pledge_to_work_with_cc(username="dataunbound", password="numbers_unbound", work_id=2, card=card1,
                               preapproval_amount='10', premium_id='150')

        # we should have an exception when the charge was attempted
        self.assertTrue(charge_exception is not None)

        # expect to have 3 events (there is a possibility that someone else could be running tests on this stripe account at the same time)
        # events returned sorted in reverse chronological order.

        self.assertEqual(len(events), 3)
        self.assertEqual(events[0].type, 'charge.failed')
        self.assertEqual(events[1].type, 'customer.card.created')
        self.assertEqual(events[2].type, 'customer.created')

        # now feed each of the events to the IPN processor.
        ipn_url = reverse("HandleIPN", args=('stripelib',))

        for (i, event) in enumerate(events):
            r = self.client.post(ipn_url, data=json.dumps({"id": event.id}), content_type="application/json; charset=utf-8")
            self.assertEqual(r.status_code, 200)

        self.assertEqual(len(Notice.objects.filter(notice_type__label='pledge_you_have_pledged', recipient__username='dataunbound')), 1)
        self.assertEqual(len(Notice.objects.filter(notice_type__label='pledge_failed', recipient__username='dataunbound')), 1)

    def recharge_with_new_card(self):

        # mark campaign as SUCCESSFUL -- campaign for work 2
        c = Work.objects.get(id=2).last_campaign()
        c.status = 'SUCCESSFUL'
        c.save()

        # set up a good card
        card1 = card(number=TEST_CARDS[0][0], exp_month=1, exp_year='2020', cvc='123', name='dataunbound',
          address_line1="100 Jackson St.", address_line2="", address_zip="94706", address_state="CA", address_country=None)  # good card

        sc = StripeClient()
        stripe_token = sc.create_token(card=card1)

        # track start time and end time of these stipe interactions so that we can limit the window of Events to look for
        time0 = stripe_token['created']

        r = self.client.post("/accounts/manage/", data={'stripe_token':stripe_token.id}, follow=True)

        #time1 = time.time()

        # retrieve events from this period -- need to pass in ints for event creation times
        events = list(sc._all_objs('Event', created={'gte': time0}))

        # now feed each of the events to the IPN processor.
        ipn_url = reverse("HandleIPN", args=('stripelib',))

        for (i, event) in enumerate(events):
            r = self.client.post(ipn_url, data=json.dumps({"id": event.id}), content_type="application/json; charset=utf-8")
            self.assertEqual(r.status_code, 200)

        # a charge should now go through
        self.assertEqual(len(Notice.objects.filter(notice_type__label='pledge_charged', recipient__username='dataunbound')), 1)


    def test_good_bad_cc_scenarios(self):
        self.verify_setup()
        self.do_test_junk_webhook()
        self.good_cc_scenario()
        self.bad_cc_scenario()
        self.recharge_with_new_card()
        self.stripe_token_none()
        self.assertEqual(len(mail.outbox), 9)

        # expect these 6 notices :
        # u'pledge_charged', <User: dataunbound>,
        # u'pledge_failed', <User: dataunbound>,
        # u'new_wisher', <User: hmelville>,
        # u'pledge_you_have_pledged', <User: dataunbound>,
        # u'pledge_charged', <User: RaymondYee>,
        # u'pledge_you_have_pledged', <User: RaymondYee>,
        # plus two customer creation emails

    def stripe_token_none(self):
        """Test that if an empty stripe_token is submitted to pledge page, we catch that issue and present normal error page to user"""

        username = "hmelville"
        password = "gofish!"
        work_id = 1
        preapproval_amount = '10'
        premium_id = '150'

        self.assertTrue(self.client.login(username=username, password=password))

        # Pro Web 2.0 Mashups
        self.work = Work.objects.get(id=work_id)
        r = self.client.get("/work/%s/" % (self.work.id))

        r = self.client.get("/work/%s/" % self.work.id)
        self.assertEqual(r.status_code, 200)

        # go to pledge page
        r = self.client.get("/pledge/%s" % self.work.id, data={}, follow=True)
        self.assertEqual(r.status_code, 200)

        # submit to pledge page
        r = self.client.post("/pledge/%s/" % self.work.id, data={'preapproval_amount': preapproval_amount,
                                                                'premium_id':premium_id}, follow=True)
        self.assertEqual(r.status_code, 200)

        # Should now be on the fund page
        pledge_fund_path = r.request.get('PATH_INFO')
        self.assertTrue(pledge_fund_path.startswith('/payment/fund'))
        # pull out the transaction info
        t_id = int(pledge_fund_path.replace('/payment/fund/',''))

        stripe_token = ''

        r = self.client.post(pledge_fund_path, data={'stripe_token':stripe_token}, follow=True)
        self.assertEqual(r.status_code, 200)

