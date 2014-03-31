"""
external library imports
"""
import logging
import os
import time
import traceback

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
from django.utils import unittest

"""
regluit imports
"""
from regluit.core.models import Campaign, Wishlist, Work
from regluit.core.signals import handle_transaction_charged
from regluit.payment.manager import PaymentManager
from regluit.payment.models import Transaction, Account
from regluit.payment.parameters import *
from regluit.utils.localdatetime import now

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
    
    print "LOGIN SANDBOX"
    
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
        print "AUTHORIZE SANDBOX"
    else:
        print "PAY SANDBOX"
    
    try:
        # We need this sleep to make sure the JS engine is finished from the sandbox loging page
        time.sleep(sleep_time)    

        if not already_at_url:
            selenium.get(url)
            print "Opened URL %s" % url
   
        try:
            # Button is only visible if the login box is NOT open
            # If the login box is open, the email/pw fiels are already accessible
            login_element = WebDriverWait(selenium, 10).until(lambda d : d.find_element_by_id("loadLogin"))
            login_element.click()

            # This sleep is needed for js to slide the buyer login into view.  The elements are always in the DOM
            # so selenium can find them, but we need them in view to interact
            time.sleep(sleep_time)
        except:
            print "Ready for Login"

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
    
    print "Tranasction Complete"
    
def payAmazonSandbox(sel):
    
        print "Expected title: {0} \n Actual Title: {1}".format('Amazon.com Sign In', sel.title)
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
        print "Expected title: {0} \n Actual Title: {1}".format('Amazon Payments', sel.title)        
        print "looking for credit_card_confirm", sel.current_url
        credit_card_confirm = WebDriverWait(sel,20).until(lambda d: d.find_elements_by_css_selector("input[type='image']"))
        credit_card_confirm[-1].click()
        
        #print "looking for payment_confirm", sel.current_url
        #payment_confirm = WebDriverWait(sel,20).until(lambda d: d.find_elements_by_css_selector("input[type='image']"))
        #print "payment_confirm ", payment_confirm
        #print "len(payment_confirm)", len(payment_confirm)
        #time.sleep(1)
        #payment_confirm[-1].click()
        
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
        self.assertEqual(t.receiver_set.all()[0].amount, t.amount)
        self.assertEqual(t.receiver_set.all()[0].currency, t.currency)
        # self.assertNotEqual(t.ref1Gerence, None)
        self.assertEqual(t.error, None)
        self.assertEqual(t.status, IPN_PAY_STATUS_CREATED)
        
        valid = URLValidator(verify_exists=True)
        try:
            valid(url)
        except ValidationError, e:
            print e

    def tearDown(self):
        self.selenium.quit()
        
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
        except ValidationError, e:
            print e
        
    def test_authorize(self):
        
        print "RUNNING TEST: test_authorize"
        
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
        c = Campaign(target=D('1000.00'),deadline=now() + timedelta(days=180),work=w)
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
        self.assertEqual(user.profile.badges.all()[0].name,'pledger')
        
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
        
        c = Campaign(target=D('1000.00'),deadline=now() + timedelta(days=180),work=w)
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

class BasicGuiTest(TestCase):
    def setUp(self):
        self.verificationErrors = []
        # This is an empty array where we will store any verification errors
        # we find in our tests

        setup_selenium()
        self.TEST_SERVER_URL = "http://ry-dev.dyndns.org"
        self.selenium = webdriver.Firefox()
        set_test_logging()
    def testFrontPage(self):
        sel = self.selenium
        sel.get(self.TEST_SERVER_URL)
        # if we click on the learn more, does the panel expand?
        # click on a id=readon -- or the Learn More span
        #sel.find_elements_by_css_selector('a#readon')[0].click()
        #time.sleep(2.0)
        # the learn more panel should be displayed
        #self.assertTrue(sel.find_elements_by_css_selector('div#user-block-hide')[0].is_displayed())
        # click on the panel again -- and panel should not be displayed
        #sel.find_elements_by_css_selector('a#readon')[0].click()
        #time.sleep(2.0)
        #self.assertFalse(sel.find_elements_by_css_selector('div#user-block-hide')[0].is_displayed())
    def tearDown(self):
        self.selenium.quit()


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
                
        user = User.objects.all()[0]            
        
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
        
       
