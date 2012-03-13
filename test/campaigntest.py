from regluit.core import models
from regluit.payment.models import Transaction, PaymentResponse, Receiver
from regluit.payment.manager import PaymentManager
from regluit.payment.paypal import IPN_PAY_STATUS_ACTIVE, IPN_PAY_STATUS_INCOMPLETE, IPN_PAY_STATUS_COMPLETED

import logging


def set_test_logging():
    
    # Setup debug logging to our console so we can watch
    defaultLogger = logging.getLogger('')
    defaultLogger.addHandler(logging.StreamHandler())
    defaultLogger.setLevel(logging.DEBUG)
    
    # Set the selenium logger to info
    sel = logging.getLogger("selenium")
    sel.setLevel(logging.INFO)
    
    
def run_google_rc():

    from selenium import selenium
    import unittest, time, re
    
    class google_rc(unittest.TestCase):
        def setUp(self):
            self.verificationErrors = []
            self.selenium = selenium("localhost", 4444, "*firefox", "https://www.google.com/")
            self.selenium.start()
        
        def test_google_rc(self):
            sel = self.selenium
            sel.open("/")
            sel.type("//input[@type='text']", "Bach")
            sel.click("name=btnG")
            time.sleep(3)
            try: self.failUnless(sel.is_text_present("Wikipedia"))
            except AssertionError, e: self.verificationErrors.append(str(e))
        
        def tearDown(self):
            self.selenium.stop()
            self.assertEqual([], self.verificationErrors)
    
    testcases = [google_rc]
    suites = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(testcase) for testcase in testcases])
    unittest.TextTestRunner().run(suites)
    
def run_google_wd():
    """
    A google example using WebDriver
    """
    
    from selenium import selenium, webdriver
    from selenium.common.exceptions import NoSuchElementException
    import unittest, time, re
    
    class GoogleWebDriverTest(unittest.TestCase):
    
        def setUp(self):
            self.verificationErrors = []
            # This is an empty array where we will store any verification errors
            # we find in our tests
    
            self.selenium = webdriver.Firefox()
            set_test_logging()
            
        def test_google_rc(self):
            sel = self.selenium
            sel.get("https://www.google.com/")
            search_box = sel.find_elements_by_xpath("//input[@type='text']")
            search_box[0].send_keys("Bach")
            search_box[0].submit()
            time.sleep(3)
            try:
                sel.find_element_by_xpath("//a[contains(@href,'wikipedia')]")
            except NoSuchElementException, e:
                self.verificationErrors.append(str(e))
            #try: self.failUnless(sel.is_text_present("Wikipedia"))
            #except AssertionError, e: self.verificationErrors.append(str(e))
        
        def tearDown(self):
            self.selenium.quit()
            self.assertEqual([], self.verificationErrors)
            
    testcases = [GoogleWebDriverTest]
    suites = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(testcase) for testcase in testcases])
    unittest.TextTestRunner().run(suites)
            
            
# from selenium import webdriver
# driver = webdriver.Remote(desired_capabilities=webdriver.DesiredCapabilities.HTMLUNITWITHJS)
# driver.get("http://google.com")

pm = PaymentManager()

def campaign_display():
    
    campaigns_with_active_transactions = models.Campaign.objects.filter(transaction__status=IPN_PAY_STATUS_ACTIVE)
    campaigns_with_incomplete_transactions = models.Campaign.objects.filter(transaction__status=IPN_PAY_STATUS_INCOMPLETE)
    campaigns_with_completed_transactions = models.Campaign.objects.filter(transaction__status=IPN_PAY_STATUS_COMPLETED)
    
    print "campaigns with active transactions", campaigns_with_active_transactions
    print "campaigns with incomplete transactions", campaigns_with_incomplete_transactions
    print "campaigns with completed transactions", campaigns_with_completed_transactions
    
def campaigns_active():
    return models.Campaign.objects.filter(transaction__status=IPN_PAY_STATUS_ACTIVE)

def campaigns_incomplete():
    return models.Campaign.objects.filter(transaction__status=IPN_PAY_STATUS_INCOMPLETE)
    
def campaigns_completed():
    return models.Campaign.objects.filter(transaction__status=IPN_PAY_STATUS_COMPLETED)

def execute_campaigns(clist):
    return [pm.execute_campaign(c) for c in clist]
    
def finish_campaigns(clist):
    return [pm.finish_campaign(c) for c in clist]

def drop_all_transactions():
    PaymentResponse.objects.all().delete()
    Receiver.objects.all().delete()
    Transaction.objects.all().delete()
    
    # go through all Campaigns and set the self.left = self.target
    for c in models.Campaign.objects.all():
        c.left = c.target
        c.save()

def recipient_status(clist):
    return [[[(r.email, r.txn_id, r.status, r.amount)  for r in t.receiver_set.all()]  for t in c.transaction_set.all()]  for c in clist]

# by the time we've executed a campaign, we should have r.status = 'COMPLETED' for primary but None for secondary
# [[[r.status  for r in t.receiver_set.all()]  for t in c.transaction_set.all()]  for c in campaigns_incomplete()]

# [[[r.status  for r in t.receiver_set.all()]  for t in c.transaction_set.all()]  for c in campaigns_completed()]

# res = [pm.finish_campaign(c) for c in campaigns_incomplete()]

