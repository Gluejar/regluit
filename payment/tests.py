"""
external library imports
"""
import logging
import os
import time
import traceback
import unittest
from unittest import mock

from datetime import timedelta
from decimal import Decimal as D
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

"""
django imports
"""
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.test import TestCase
from django.utils.timezone import now

"""
regluit imports
"""
from regluit.core.models import Campaign, Wishlist, Work
from regluit.core.parameters import REWARDS
from regluit.core.signals import handle_transaction_charged
from regluit.payment.manager import PaymentManager
from regluit.payment.models import Transaction, Account
from regluit.payment.parameters import *

def setup_selenium():
    # Set the display window for our xvfb
    os.environ['DISPLAY'] = ':99'

def set_test_logging():
    
    # Setup debug logging to our console so we can watch
    defaultLogger = logging.getLogger('')
    defaultLogger.addHandler(logging.StreamHandler())
    defaultLogger.setLevel(logging.DEBUG)
    
    # Set the selenium logger to info
    sel = logging.getLogger("selenium")
    sel.setLevel(logging.INFO)

def loginSandbox(selenium):
    
    print("LOGIN SANDBOX")
    
    try:
        selenium.get('https://developer.paypal.com/')
        login_email = WebDriverWait(selenium, 10).until(lambda d : d.find_element_by_id("login_email"))
        login_email.click()
        login_email.send_keys(settings.PAYPAL_SANDBOX_LOGIN)
        
        login_password = WebDriverWait(selenium, 10).until(lambda d : d.find_element_by_id("login_password"))
        login_password.click()
        login_password.send_keys(settings.PAYPAL_SANDBOX_PASSWORD)
        
        submit_button = WebDriverWait(selenium, 10).until(lambda d : d.find_element_by_css_selector("input[class=\"formBtnOrange\"]"))
        submit_button.click()
    
    except:
        traceback.print_exc()
    
def paySandbox(test, selenium, url, authorize=False, already_at_url=False, sleep_time=20):
    
    
    if authorize:
        print("AUTHORIZE SANDBOX")
    else:
        print("PAY SANDBOX")
    
    try:
        # We need this sleep to make sure the JS engine is finished from the sandbox loging page
        time.sleep(sleep_time)    

        if not already_at_url:
            selenium.get(url)
            print("Opened URL %s" % url)
   
        try:
            # Button is only visible if the login box is NOT open
            # If the login box is open, the email/pw fiels are already accessible
            login_element = WebDriverWait(selenium, 10).until(lambda d : d.find_element_by_id("loadLogin"))
            login_element.click()

            # This sleep is needed for js to slide the buyer login into view.  The elements are always in the DOM
            # so selenium can find them, but we need them in view to interact
            time.sleep(sleep_time)
        except:
            print("Ready for Login")

        email_element = WebDriverWait(selenium, 60).until(lambda d : d.find_element_by_id("login_email"))
        email_element.click()
        email_element.clear()
        email_element.send_keys(settings.PAYPAL_BUYER_LOGIN)
        
        password_element = WebDriverWait(selenium, 60).until(lambda d : d.find_element_by_id("login_password"))
        password_element.click()
        password_element.clear()
        password_element.send_keys(settings.PAYPAL_BUYER_PASSWORD)

        submit_button = WebDriverWait(selenium, 60).until(lambda d : d.find_element_by_id("submitLogin"))
        submit_button.click()
      
        # This sleep makes sure js has time to animate out the next page
        time.sleep(sleep_time)

        final_submit = WebDriverWait(selenium, 60).until(lambda d : d.find_element_by_id("submit.x"))
        final_submit.click()
       
        # This makes sure the processing of the final submit is complete
        time.sleep(sleep_time)

        # Don't wait too long for this, it isn't really needed.  By the time JS has gotten around to 
        # displaying this element, the redirect has usually occured       
        try:
            return_button = WebDriverWait(selenium, 10).until(lambda d : d.find_element_by_id("returnToMerchant"))
            return_button.click()
        except:
            blah = "blah"
        
    except:
        traceback.print_exc()
    
    print("Tranasction Complete")
    
def payAmazonSandbox(sel):
    
        print("Expected title: {0} \n Actual Title: {1}".format('Amazon.com Sign In', sel.title))
        # does it make sense to throw up if there is problem....what better invariants?
        login_email = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector("input#ap_email"))
        login_email.click()
        login_email.clear()
        login_email.send_keys('supporter1@raymondyee.net')
        login_password = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector("input#ap_password"))
        login_password.click()
        login_password.clear()
        login_password.send_keys('testpw__')
        submit_button = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector("input#signInSubmit"))
        submit_button.click()
        time.sleep(2)
        
        # sel.find_element_by_css_selector("input[type='image']")
        print("Expected title: {0} \n Actual Title: {1}".format('Amazon Payments', sel.title))       
        print ("looking for credit_card_confirm", sel.current_url)
        credit_card_confirm = WebDriverWait(sel,20).until(lambda d: d.find_elements_by_css_selector("input[type='image']"))
        credit_card_confirm[-1].click()

@unittest.skip("skipping PledgeTest (selenium)")
class PledgeTest(TestCase):
    
    def setUp(self):
        self.verificationErrors = []
        # This is an empty array where we will store any verification errors
        # we find in our tests

        setup_selenium()
        self.selenium = webdriver.Firefox()
        set_test_logging()

    def validateRedirect(self, t, url, count):
    
        self.assertNotEqual(url, None)
        self.assertNotEqual(t, None)
        self.assertEqual(t.receiver_set.all().count(), count)
        self.assertEqual(t.receiver_set.first().amount, t.amount)
        self.assertEqual(t.receiver_set.first().currency, t.currency)
        # self.assertNotEqual(t.ref1Gerence, None)
        self.assertEqual(t.error, None)
        self.assertEqual(t.status, IPN_PAY_STATUS_CREATED)
        
        valid = URLValidator(verify_exists=True)
        try:
            valid(url)
        except ValidationError as e:
            print(e)

    def tearDown(self):
        self.selenium.quit()

@unittest.skip("skipping AuthorizeTest (selenium)")
class AuthorizeTest(TestCase):
    
    def setUp(self):
        self.verificationErrors = []
        # This is an empty array where we will store any verification errors
        # we find in our tests

        setup_selenium()
        self.selenium = webdriver.Firefox()
        set_test_logging()
    
    def validateRedirect(self, t, url):
    
        self.assertNotEqual(url, None)
        self.assertNotEqual(t, None)
        #self.assertNotEqual(t.reference, None)
        self.assertEqual(t.error, None)
        self.assertEqual(t.status, 'NONE')
        
        valid = URLValidator(verify_exists=True)
        try:
            valid(url)
        except ValidationError as e:
            print(e)
        
    def test_authorize(self):
        
        print("RUNNING TEST: test_authorize")
        
        p = PaymentManager()
    
        # Note, set this to 1-5 different receivers with absolute amounts for each
        
        t, url = p.authorize(t)
        
        self.validateRedirect(t, url)
        
        loginSandbox(self.selenium)
        paySandbox(self, self.selenium, url, authorize=True)
    
        # stick in a getStatus to update statuses in the absence of IPNs
        p.checkStatus()
        
        t = Transaction.objects.get(id=t.id)
        
        self.assertEqual(t.status, IPN_PREAPPROVAL_STATUS_ACTIVE)
        
    def tearDown(self):
        self.selenium.quit()

class CreditTest(TestCase):
    user1=None
    user2=None
    def setUp(self):
        """
        """
        self.user1 = User.objects.create_user('credit_test1', 'support@example.org', 'credit_test1')
        self.user2 = User.objects.create_user('credit_test2', 'support+1@example.org', 'credit_test2')

    def testSimple(self):
        """
        """
        self.assertFalse(self.user1.credit.add_to_balance(-100))
        self.assertTrue(self.user1.credit.add_to_balance(100))
        self.assertTrue(self.user1.credit.add_to_pledged(50))
        self.assertFalse(self.user1.credit.add_to_pledged(60))
        self.assertFalse(self.user1.credit.use_pledge(60))
        self.assertTrue(self.user1.credit.use_pledge(50))
        self.assertFalse(self.user1.credit.transfer_to(self.user2,60))
        self.assertTrue(self.user1.credit.transfer_to(self.user2,50))
        self.assertEqual(self.user1.credit.balance, 0)
        self.assertEqual(self.user2.credit.balance, 50)

@unittest.skip("skipping ExtraTest")
class ExtraTest(TestCase):
    
    def testPledgeExtra(self):
        u= User.objects.create_user('payment_test', 'support@example.org', 'payment_test')
        t= Transaction(user=u)
        self.assertEqual(t.extra, {})
        ack_name=t.extra.get('ack_name','')
        if not ack_name:
            t.extra.update({'ack_name': t.user.username})
        self.assertEqual(t.extra, {'ack_name': 'payment_test'})
    
       
class TransactionTest(TestCase):
    fixtures=['initial_data.json']
    def setUp(self):
        """
        """
        pass
    def testSimple(self):
        """
        create a single transaction with PAYMENT_TYPE_AUTHORIZATION / ACTIVE with a $12.34 pledge and see whether the payment
        manager can query and get the right amount.
        """
        user = User.objects.create_user('payment_test', 'support@example.org', 'payment_test')

        w = Work()
        w.save()
        c = Campaign(target=D('1000.00'),deadline=now() + timedelta(days=180),work=w,
                     # legacy pledge transaction: pin type now that the default is THANKS (#1195)
                     type=REWARDS)
        c.save()
        
        t = Transaction()
        t.amount = D('12.34')
        t.type = PAYMENT_TYPE_AUTHORIZATION
        t.status = 'ACTIVE'
        t.approved = True
        t.campaign = c
        t.user = user
        t.save()
        
        #test pledge adders
        user.profile.reset_pledge_badge()
        self.assertEqual(user.profile.badges.first().name,'pledger')
        
        p = PaymentManager()
        results = p.query_campaign(c,campaign_total=True, summary=False)
        self.assertEqual(results[0].amount, D('12.34'))
        self.assertEqual(c.left,c.target-D('12.34'))
        self.assertEqual(c.supporters_count, 1)
        
    def test_paymentmanager_charge(self):
        """
        test regluit.payment.manager.PaymentManager.charge
        
        trying to simulate the conditions of having a bare transaction setup before we try to do
        an instant charge.
        
        """
        user = User.objects.create_user('pm_charge', 'support2@example.org', 'payment_test')
        # need to create an Account to associate with user
        from regluit.payment.stripelib import StripeClient, card, Processor
        
        sc = StripeClient()
        
        # valid card and Account
        card0 = card()
        stripe_processor = Processor()
        account = stripe_processor.make_account(user=user,token=card0)

        w = Work()
        w.save()
        
        c = Campaign(target=D('1000.00'),deadline=now() + timedelta(days=180),work=w,
                     # legacy pledge transaction: pin type now that the default is THANKS (#1195)
                     type=REWARDS)
        c.save()
        
        t = Transaction(host='stripelib')
        
        t.max_amount = D('12.34')
        t.type = PAYMENT_TYPE_NONE
        t.status = TRANSACTION_STATUS_NONE
        t.campaign = c
        t.approved = False
        t.user = user
        
        t.save()
        
        pm = PaymentManager()
        response = pm.charge(t)
        
        self.assertEqual(t.status, TRANSACTION_STATUS_COMPLETE)
        self.assertEqual(t.type, EXECUTE_TYPE_CHAINED_INSTANT)
        self.assertEqual(t.amount, D('12.34'))

# class BasicGuiTest(TestCase):
#     def setUp(self):
#         self.verificationErrors = []
#         # This is an empty array where we will store any verification errors
#         # we find in our tests

#         setup_selenium()
#         self.TEST_SERVER_URL = "http://ry-dev.dyndns.org"
#         self.selenium = webdriver.Firefox()
#         set_test_logging()
#     def testFrontPage(self):
#         sel = self.selenium
#         sel.get(self.TEST_SERVER_URL)
#         # if we click on the learn more, does the panel expand?
#         # click on a id=readon -- or the Learn More span
#         #sel.find_elements_by_css_selector('a#readon')[0].click()
#         #time.sleep(2.0)
#         # the learn more panel should be displayed
#         #self.assertTrue(sel.find_elements_by_css_selector('div#user-block-hide')[0].is_displayed())
#         # click on the panel again -- and panel should not be displayed
#         #sel.find_elements_by_css_selector('a#readon')[0].click()
#         #time.sleep(2.0)
#         #self.assertFalse(sel.find_elements_by_css_selector('div#user-block-hide')[0].is_displayed())
#     def tearDown(self):
#         self.selenium.quit()


class AccountTest(TestCase):
    
    @staticmethod       
    def get_transaction_level():
        from django.db import connection
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM information_schema.global_variables WHERE variable_name='tx_isolation';")
        row = cursor.fetchone()
        return row
     
    
    def test_status_changes(self):
        
        from regluit.core.models import UserProfile
        
        user1 = User.objects.create_user('account_test1', 'account_test1@gluejar.com', 'account_test1_pw')
        user1.save()
        
        account1 = Account(host='host1', account_id='1', user=user1, status='ACTIVE')
        account1.save()
                
        user = User.objects.first()           
        
        account = user1.profile.account
        self.assertEqual(account.status, 'ACTIVE')
        account.status = 'EXPIRING'
        account.save()
        
        self.assertEqual(account.status, 'EXPIRING')
        account.save()
        
        user1.delete()
        account1.delete()
    
def suite():

    #testcases = [PledgeTest, AuthorizeTest, TransactionTest]
    testcases = [TransactionTest, CreditTest, AccountTest]
    suites = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(testcase) for testcase in testcases])
    return suites    
        
       


class StripeWebhookCourtesyEmailTest(TestCase):
    """#1216: a failing courtesy email must not 500 the Stripe webhook.

    The customer.created handler sends an FYI email to support synchronously.
    Before the guard, any transient mail failure (observed live 2026-08-23: an
    intermittent SES auth error) escaped ProcessIPN, the webhook returned 500,
    and Stripe re-delivered the event on backoff for days — re-attempting the
    same send and emailing ADMINS a traceback on every retry.
    """

    def _post_event(self):
        from django.test import RequestFactory
        return RequestFactory().post(
            "/handleipn/stripelib",
            data='{"id": "evt_test_1216"}',
            content_type="application/json",
        )

    def _fake_event(self):
        class _Obj(dict):
            pass
        event = mock.MagicMock()
        event.get = {"type": "customer.created"}.get
        data = mock.MagicMock()
        data.object = _Obj(
            {"id": "cus_test", "description": "test", "email": "t@example.org"})
        event.data = data
        return event

    def test_mail_failure_does_not_500_the_webhook(self):
        from regluit.payment import stripelib

        with mock.patch.object(stripelib, "StripeClient") as sc:
            sc.return_value.event.retrieve.return_value = self._fake_event()
            with mock.patch.object(
                    stripelib, "send_mail",
                    side_effect=Exception("SES transient auth failure")):
                response = stripelib.Processor().ProcessIPN(self._post_event())
        self.assertEqual(response.status_code, 200)

    def test_mail_success_still_sends(self):
        from regluit.payment import stripelib

        with mock.patch.object(stripelib, "StripeClient") as sc:
            sc.return_value.event.retrieve.return_value = self._fake_event()
            with mock.patch.object(stripelib, "send_mail") as sent:
                response = stripelib.Processor().ProcessIPN(self._post_event())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(sent.call_count, 1)


class AnonymousStripeCustomerBugTest(TestCase):
    """#1125: a logged-in donor's Stripe Customer must not be created as
    'anonymous user'.

    Reproduces FundView.form_valid's actual call shape for a one-off
    donation: transaction.user is set to the authenticated donor, but a
    Stripe.js card token is still passed through to
    PaymentManager.charge(..., token=...) because the donor doesn't have an
    Account yet. Pay.__init__ used to key off token-presence alone to decide
    "user is anonymous", so it called make_account() without the user and
    every such donation produced a Stripe Customer described as "anonymous
    user" with no Account linked back to the donor's profile.

    Uses this repo's mocked-Stripe pattern (see StripeWebhookCourtesyEmailTest
    above) rather than a live call to the Stripe test-mode API.
    """

    def _fake_customer(self, customer_id='cus_test_1125'):
        customer = mock.MagicMock()
        customer.id = customer_id
        customer.active_card.last4 = '4242'
        customer.active_card.type = 'Visa'
        customer.active_card.exp_month = 1
        customer.active_card.exp_year = 2030
        customer.active_card.fingerprint = 'fp_test_1125'
        customer.active_card.country = 'US'
        return customer

    def _make_transaction(self, user):
        # No campaign -- this mirrors FundView.form_valid's plain-donation
        # branch (`if not self.transaction.campaign:`), the actual code path
        # #1125 was filed against.
        t = Transaction(host='stripelib')
        t.max_amount = D('5.00')
        t.type = PAYMENT_TYPE_NONE
        t.status = TRANSACTION_STATUS_NONE
        t.campaign = None
        t.approved = False
        t.user = user
        t.save()
        return t

    def test_logged_in_donation_creates_identified_customer(self):
        """Mirrors FundView.form_valid: transaction.user is the authenticated
        donor AND a token is passed to charge() (no Account exists yet)."""
        from regluit.payment import stripelib

        user = User.objects.create_user(
            'donor_1125', 'donor_1125@example.org', 'payment_test')
        t = self._make_transaction(user)
        # A Stripe.js-token-shaped string (as FundView actually passes --
        # the raw dict-of-card-fields shape is only used by the legacy
        # live-API test elsewhere in this file), so the
        # create_customer/create_charge assertions below mean something.
        # Not a real credential -- StripeClient is fully mocked below.
        card_ref = 'card-ref-test-1125'

        with mock.patch.object(stripelib, "StripeClient") as sc:
            sc.return_value.create_customer.return_value = self._fake_customer()
            sc.return_value.create_charge.return_value.id = 'ch_test_1125'
            pm = PaymentManager()
            pm.charge(t, token=card_ref)

        _, kwargs = sc.return_value.create_customer.call_args
        self.assertEqual(kwargs.get('card'), card_ref)
        self.assertEqual(kwargs.get('description'), user.username)
        self.assertEqual(kwargs.get('email'), user.email)

        account = Account.objects.get(account_id='cus_test_1125')
        self.assertEqual(account.user, user)

        # Codex round-1 (#1247): a failure after Customer creation must not
        # go unnoticed -- pin down that the charge actually landed on the
        # Customer this call just created, and that the transaction is
        # left fully complete.
        _, charge_kwargs = sc.return_value.create_charge.call_args
        self.assertEqual(charge_kwargs.get('customer'), 'cus_test_1125')

        t.refresh_from_db()
        self.assertEqual(t.status, TRANSACTION_STATUS_COMPLETE)
        self.assertEqual(t.pay_key, 'ch_test_1125')

    def test_truly_anonymous_donation_still_anonymous(self):
        """No transaction.user at all -- must keep the pre-existing
        anonymous-customer behavior (email from transaction.receipt, no
        Account.user)."""
        from regluit.payment import stripelib

        t = self._make_transaction(user=None)
        t.receipt = 'anon_1125@example.org'
        t.save()

        with mock.patch.object(stripelib, "StripeClient") as sc:
            sc.return_value.create_customer.return_value = self._fake_customer(
                customer_id='cus_test_1125_anon')
            sc.return_value.create_charge.return_value.id = 'ch_test_1125_anon'
            pm = PaymentManager()
            pm.charge(t, token={
                "number": "4242424242424242", "exp_month": 1, "exp_year": 2030})

        _, kwargs = sc.return_value.create_customer.call_args
        self.assertEqual(kwargs.get('description'), 'anonymous user')
        self.assertEqual(kwargs.get('email'), 'anon_1125@example.org')

        account = Account.objects.get(account_id='cus_test_1125_anon')
        self.assertIsNone(account.user)
