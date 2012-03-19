from regluit.core import models
from regluit.payment.models import Transaction, PaymentResponse, Receiver
from regluit.payment.manager import PaymentManager
from regluit.payment.paypal import IPN_PAY_STATUS_ACTIVE, IPN_PAY_STATUS_INCOMPLETE, IPN_PAY_STATUS_COMPLETED

from django.conf import settings

from selenium import selenium, webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re

import logging
import os


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
    
    

class GoogleWebDriverTest(unittest.TestCase):

    def setUp(self):
        setup_selenium()
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
    
    def tearDown(self):
        self.selenium.quit()
        self.assertEqual([], self.verificationErrors)

def run_google_rc():
    """
    """

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

def support_campaign():
    """
    programatically fire up selenium to make a Pledge
    """
    UNGLUE_IT_URL = settings.LIVE_SERVER_TEST_URL
    # unglue.it login
    USER = settings.UNGLUEIT_TEST_USER
    PASSWORD = settings.UNGLUEIT_TEST_PASSWORD
    
    # PayPal developer sandbox
    from regluit.payment.tests import loginSandbox, paySandbox
    
    setup_selenium()
    
    # we can experiment with different webdrivers
    #sel = webdriver.Firefox()
    
    # Chrome
    sel = webdriver.Chrome(executable_path='/Users/raymondyee/C/src/Gluejar/regluit/test/chromedriver')
    
    # HTMLUNIT with JS -- not successful
    #sel = webdriver.Remote("http://localhost:4444/wd/hub", webdriver.DesiredCapabilities.HTMLUNITWITHJS)

    time.sleep(5)
    
    # find a campaign to pledge to
    loginSandbox(sel)

    time.sleep(2)
    print "now opening unglue.it"
    
    #sel.get("http://www.google.com")
    sel.get(UNGLUE_IT_URL)
    
    # long wait because sel is slow after PayPal
    sign_in_link = WebDriverWait(sel, 100).until(lambda d : d.find_element_by_xpath("//span[contains(text(),'Sign In')]/.."))
    sign_in_link.click()

    # enter login
    input_username = WebDriverWait(sel,20).until(lambda d : d.find_element_by_css_selector("input#id_username"))
    input_username.send_keys(USER)
    sel.find_element_by_css_selector("input#id_password").send_keys(PASSWORD)
    sel.find_element_by_css_selector("input[value*='sign in']").click()
    
    # click on biggest campaign list
    biggest_campaign_link = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector("a[href*='/campaigns/pledged']"))
    biggest_campaign_link.click()
    time.sleep(1)
    
    # pull up one of the campaigns to pledge to
    # div.book-list div.title a
    # for now, take the first book and click on the link to get to the work page
    sel.find_elements_by_css_selector("div.book-list div.title a")[0].click()
    
    time.sleep(1)
    sel.find_element_by_css_selector("input[value*='Support']").click()
    
    # just click Pledge without filling out amount -- should have the form validation spot the error
    pledge_button = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector("input[value*='Pledge']"))
    pledge_button.click()
    # check to see whether there is an error
    error_messages = WebDriverWait(sel,20).until(lambda d: d.find_elements_by_css_selector("ul.errorlist"))
    if len(error_messages):
        print "yes:  Error in just hitting pledge button as expected"
    else:
        print "ooops:  there should be an error message when pledge button hit"
    
    # enter a $10 pledge
    preapproval_amount_input = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector("input#id_preapproval_amount"))
    preapproval_amount_input.send_keys("10")
    pledge_button = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector("input[value*='Pledge']"))
    pledge_button.click()
    
    # grab the URL where sel is now?
    
    print  "Now trying to pay PayPal", sel.current_url
    paySandbox(None, sel, sel.current_url, authorize=True, already_at_url=True, sleep_time=5)
    
    #sel.quit()
    

def suites():
    testcases = [GoogleWebDriverTest]
    suites = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(testcase) for testcase in testcases])
    

