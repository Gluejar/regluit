"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.utils import unittest
from regluit.payment.manager import PaymentManager
from regluit.payment.paypal import IPN, IPN_PAY_STATUS_ACTIVE, IPN_PAY_STATUS_COMPLETED, IPN_TXN_STATUS_COMPLETED
from noseselenium.cases import SeleniumTestCaseMixin
from regluit.payment.models import Transaction
from regluit.core.models import Campaign, Wishlist, Work
from django.contrib.auth.models import User
from regluit.payment.parameters import *
import traceback
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import time
from selenium import selenium, webdriver

from decimal import Decimal as D
import datetime

def loginSandbox(test, selenium):
    
    print "LOGIN SANDBOX"
    
    try:
        selenium.open('https://developer.paypal.com/')
        time.sleep(5)
        test.failUnless(selenium.is_text_present('Member Log In'))
        selenium.type('login_email', PAYPAL_SANDBOX_LOGIN)
        selenium.type('login_password', PAYPAL_SANDBOX_PASSWORD)
        time.sleep(2)
        selenium.click('css=input[class=\"formBtnOrange\"]')
        time.sleep(5)
        test.failUnless(selenium.is_text_present('Test Accounts'))
    except:
        traceback.print_exc()
    
def authorizeSandbox(test, selenium, url):
    
    print "AUTHORIZE SANDBOX"
    
    try:
        selenium.open(url)
        time.sleep(5)
        test.failUnless(selenium.is_text_present('Your preapproved payment summary'))
        selenium.click('loadLogin')
        time.sleep(5)
        selenium.type('id=login_email', PAYPAL_BUYER_LOGIN)
        selenium.type('id=login_password', PAYPAL_BUYER_PASSWORD)
        time.sleep(2)
        selenium.click('submitLogin')
        time.sleep(5)
        test.failUnless(selenium.is_text_present('Review your information'))
        selenium.click('submit.x')
        time.sleep(10)
        selenium.click('returnToMerchant')
        time.sleep(15)
        
    except:
        traceback.print_exc()
def paySandbox(test, selenium, url):
    
    print "PAY SANDBOX"
    
    try:
        selenium.open(url)
        time.sleep(5)
        test.failUnless(selenium.is_text_present('Your payment summary'))
        selenium.click('loadLogin')
        time.sleep(5)
        selenium.type('id=login_email', PAYPAL_BUYER_LOGIN)
        selenium.type('id=login_password', PAYPAL_BUYER_PASSWORD)
        time.sleep(2)
        selenium.click('submitLogin')
        time.sleep(5)
        test.failUnless(selenium.is_text_present('Review your information'))
        selenium.click('submit.x')
        time.sleep(10)
        selenium.click('returnToMerchant')
        time.sleep(15)
        
    except:
        traceback.print_exc()
    
class PledgeTest(TestCase):
    
    def setUp(self):
        self.verificationErrors = []
        # This is an empty array where we will store any verification errors
        # we find in our tests

        self.selenium = selenium("localhost", 4444, "*firefox",
                "http://www.google.com/")
        self.selenium.start()

    
    def validateRedirect(self, t, url, count):
    
        self.assertNotEqual(url, None)
        self.assertNotEqual(t, None)
        self.assertEqual(t.receiver_set.all().count(), count)
        self.assertEqual(t.receiver_set.all()[0].amount, t.amount)
        self.assertEqual(t.receiver_set.all()[0].currency, t.currency)
        self.assertNotEqual(t.reference, None)
        self.assertEqual(t.error, None)
        self.assertEqual(t.status, 'NONE')
        
        valid = URLValidator(verify_exists=True)
        try:
            valid(url)
        except ValidationError, e:
            print e
        
    
    def test_pledge_single_receiver(self):
        
        try:
            p = PaymentManager()
    
            # Note, set this to 1-5 different receivers with absolute amounts for each
            receiver_list = [{'email':'jakace_1309677337_biz@gmail.com', 'amount':20.00}]
            t, url = p.pledge('USD', TARGET_TYPE_NONE, receiver_list, campaign=None, list=None, user=None)
        
            self.validateRedirect(t, url, 1)
        
            loginSandbox(self, self.selenium)
            paySandbox(self, self.selenium, url)
            
            t = Transaction.objects.get(id=t.id)
        
            # by now we should have received the IPN
            self.assertEqual(t.status, IPN_PAY_STATUS_COMPLETED)
            self.assertEqual(t.receiver_set.all()[0].status, IPN_TXN_STATUS_COMPLETED)
            
        except:
            traceback.print_exc()
        
    def test_pledge_mutiple_receiver(self):
        
        p = PaymentManager()
    
        # Note, set this to 1-5 different receivers with absolute amounts for each
        receiver_list = [{'email':'jakace_1309677337_biz@gmail.com', 'amount':20.00}, 
                         {'email':'seller_1317463643_biz@gmail.com', 'amount':10.00}]
        
        t, url = p.pledge('USD', TARGET_TYPE_NONE, receiver_list, campaign=None, list=None, user=None)
        
        self.validateRedirect(t, url, 2)
        
        loginSandbox(self, self.selenium)
        paySandbox(self, self.selenium, url)
        
        t = Transaction.objects.get(id=t.id)
        
        # by now we should have received the IPN
        self.assertEqual(t.status, IPN_PAY_STATUS_COMPLETED)
        self.assertEqual(t.receiver_set.all()[0].status, IPN_TXN_STATUS_COMPLETED)
        self.assertEqual(t.receiver_set.all()[1].status, IPN_TXN_STATUS_COMPLETED)
    
    def test_pledge_too_much(self):
        
        p = PaymentManager()
    
        # Note, set this to 1-5 different receivers with absolute amounts for each
        receiver_list = [{'email':'jakace_1309677337_biz@gmail.com', 'amount':50000.00}]
        t, url = p.pledge('USD', TARGET_TYPE_NONE, receiver_list, campaign=None, list=None, user=None)
        
        self.validateRedirect(t, url, 1)
        
class AuthorizeTest(TestCase):
    
    def setUp(self):
        self.verificationErrors = []
        # This is an empty array where we will store any verification errors
        # we find in our tests

        self.selenium = selenium("localhost", 4444, "*firefox",
                "http://www.google.com/")
        self.selenium.start()
    
    def validateRedirect(self, t, url):
    
        self.assertNotEqual(url, None)
        self.assertNotEqual(t, None)
        self.assertNotEqual(t.reference, None)
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
        
        t, url = p.authorize('USD', TARGET_TYPE_NONE, 100.0, campaign=None, list=None, user=None)
        
        self.validateRedirect(t, url)
        
        loginSandbox(self, self.selenium)
        authorizeSandbox(self, self.selenium, url)
    
        t = Transaction.objects.get(id=t.id)
        
        self.assertEqual(t.status, IPN_PAY_STATUS_ACTIVE)
        
class TransactionTest(TestCase):
    def setUp(self):
        """
        """
        pass
    def testSimple(self):
        """
        create a single transaction with PAYMENT_TYPE_INSTANT / COMPLETED with a $12.34 pledge and see whether the payment
        manager can query and get the right amount.
        """
        
        w = Work()
        w.save()
        c = Campaign(target=D('1000.00'),deadline=datetime.datetime.utcnow() + datetime.timedelta(days=180),work=w)
        c.save()
        
        t = Transaction()
        t.amount = D('12.34')
        t.type = PAYMENT_TYPE_AUTHORIZATION
        t.status = 'ACTIVE'
        t.campaign = c
        t.save()
        
        p = PaymentManager()
        results = p.query_campaign(campaign=c)
        self.assertEqual(results[0].amount, D('12.34'))
        self.assertEqual(c.left,c.target-D('12.34'))

def suite():

    #testcases = [PledgeTest, AuthorizeTest]
    testcases = [TransactionTest]
    suites = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(testcase) for testcase in testcases])
    
    return suites    
        
       