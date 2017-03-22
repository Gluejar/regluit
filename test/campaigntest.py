"""
external library imports
"""
import logging
import os
import re
import time
import unittest
from urlparse import (urlparse, urlunparse)

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

"""
django imports
"""
import django
from django.conf import settings

"""
regluit imports
"""
from regluit.core import models
from regluit.payment import stripelib
from regluit.payment.manager import PaymentManager
from regluit.payment.models import Transaction, PaymentResponse, Receiver

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
    
    
def selenium_driver(browser='firefox'):

    if browser == 'firefox':
        firefox_capabilities = DesiredCapabilities.FIREFOX
        #firefox_capabilities['marionette'] = True
        firefox_capabilities['binary'] = settings.FIREFOX_PATH
        driver = webdriver.Firefox(capabilities=firefox_capabilities)
    elif browser == 'htmlunit':
        # HTMLUNIT with JS -- not successful
        driver = webdriver.Remote("http://localhost:4444/wd/hub", webdriver.DesiredCapabilities.HTMLUNITWITHJS)
    else:
        driver = webdriver.Chrome(executable_path=settings.CHROMEDRIVER_PATH)

    return driver


class GoogleWebDriverTest(unittest.TestCase):

    def setUp(self):
        setup_selenium()
        self.verificationErrors = []
        # This is an empty array where we will store any verification errors
        # we find in our tests

        self.selenium = selenium_driver(browser='firefox')
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

    #from selenium import selenium
    import selenium
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
    
    campaigns_with_active_transactions = models.Campaign.objects.filter(transaction__status=IPN_PREAPPROVAL_STATUS_ACTIVE)
    campaigns_with_incomplete_transactions = models.Campaign.objects.filter(transaction__status=IPN_PAY_STATUS_INCOMPLETE)
    campaigns_with_completed_transactions = models.Campaign.objects.filter(transaction__status=IPN_PAY_STATUS_COMPLETED)
    
    print "campaigns with active transactions", campaigns_with_active_transactions
    print "campaigns with incomplete transactions", campaigns_with_incomplete_transactions
    print "campaigns with completed transactions", campaigns_with_completed_transactions
    
def campaigns_active():
    return models.Campaign.objects.filter(transaction__status=IPN_PREAPPROVAL_STATUS_ACTIVE)

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

def test_relaunch(unglue_it_url = settings.LIVE_SERVER_TEST_URL, do_local=True, backend='amazon', browser='firefox'):

    # django.db.transaction.enter_transaction_management()

    UNGLUE_IT_URL = unglue_it_url
    USER = settings.UNGLUEIT_TEST_USER
    PASSWORD = settings.UNGLUEIT_TEST_PASSWORD
    
    setup_selenium()
    
    sel = selenium_driver(browser=browser)

    time.sleep(5)
    
    print "now opening unglue.it"
    
    #sel.get("http://www.google.com")
    sel.get(UNGLUE_IT_URL)    
    
    # long wait because sel is slow after PayPal
    sign_in_link = WebDriverWait(sel, 100).until(lambda d : d.find_element_by_xpath("//span[contains(text(),'Sign In')]/.."))
    sign_in_link.click()

    # enter unglue.it login info
    input_username = WebDriverWait(sel,20).until(lambda d : d.find_element_by_css_selector("input#id_username"))
    input_username.send_keys(USER)
    sel.find_element_by_css_selector("input#id_password").send_keys(PASSWORD)
    sel.find_element_by_css_selector("input[value*='Sign in with Password']").click()    
    
    # click on biggest campaign list
    # I have no idea why selenium thinks a is not displayed....so that's why I'm going up one element.
    # http://stackoverflow.com/a/6141678/7782
    #biggest_campaign_link = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector("li > a[href*='/campaigns/ending']"))
    #biggest_campaign_link.click()
    #time.sleep(1)
    
    yield sel

    # jump to /campaigns/ending#2
    p = list(urlparse(UNGLUE_IT_URL)); p[2] = '/campaigns/ending#2'
    sel.get(urlunparse(p))
    time.sleep(1)
    
    # pull up one of the campaigns to pledge to
    # for now, take the first book and click on the link to get to the work page

    work_links = WebDriverWait(sel,10).until(lambda d: d.find_elements_by_css_selector("div.book-list div.title a"))
    time.sleep(2)
    work_links[0].click()
    time.sleep(2)
    
    support_button = WebDriverWait(sel,10).until(lambda d: d.find_element_by_css_selector("input[value*='Pledge']"))
    support_button.click()
    
    # just click Pledge button without filling out amount -- should have the form validation spot the error
    pledge_button = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector("input[value*='Pledge']"))
    pledge_button.click()
    # check to see whether there is an error
    error_messages = WebDriverWait(sel,20).until(lambda d: d.find_elements_by_css_selector("ul.errorlist"))
    if len(error_messages):
        print "yes:  Error in just hitting pledge button as expected"
    else:
        print "ooops:  there should be an error message when pledge button hit"
    
    print "making $10 pledge"
    
    # now we have to replace the current preapproval amount with 10
    sel.execute_script("""document.getElementById("id_preapproval_amount").value="10";""")
    
    support_button = WebDriverWait(sel,10).until(lambda d: d.find_element_by_css_selector("input[value*='Pledge Now']"))
    support_button.click()    
    
    ## now fill out the credit card
    ## CVC should fail but doesn't for now -- hmmm.
    #
    #sel.execute_script("""document.getElementById("card_Number").value={0};""".format(stripelib.ERROR_TESTING['CVC_CHECK_FAIL'][0]))
    #sel.execute_script("""document.getElementById("card_ExpiryMonth").value="01";""")
    #sel.execute_script("""document.getElementById("card_ExpiryYear").value="14";""")
    #sel.execute_script("""document.getElementById("card_CVC").value="123";""")
    #
    #verify_cc_button = WebDriverWait(sel,10).until(lambda d: d.find_element_by_css_selector("input[value*='Complete Pledge']"))
    #verify_cc_button.click()
    #
    #yield sel
    
    # let's put in a Luhn-invalid # e.g., 4242424242424241
    sel.execute_script("""document.getElementById("card_Number").value="4242424242424241";""")
    sel.execute_script("""document.getElementById("card_ExpiryMonth").value="01";""")
    sel.execute_script("""document.getElementById("card_ExpiryYear").value="18";""")
    sel.execute_script("""document.getElementById("card_CVC").value="321";""")
    
    verify_cc_button = WebDriverWait(sel,10).until(lambda d: d.find_element_by_css_selector("input[value*='Complete Pledge']"))
    verify_cc_button.click()    
       
    # should do a check for "Your card number is incorrect" -- but this doesn't stall -- so we're ok
    time.sleep(2)
    
    # should succeed
    sel.execute_script("""document.getElementById("card_Number").value={0};""".format(stripelib.TEST_CARDS[0][0]))
    sel.execute_script("""document.getElementById("card_ExpiryMonth").value="01";""")
    sel.execute_script("""document.getElementById("card_ExpiryYear").value="18";""")
    sel.execute_script("""document.getElementById("card_CVC").value="321";""")
    
    time.sleep(2)
    
    verify_cc_button = WebDriverWait(sel,10).until(lambda d: d.find_element_by_css_selector("input[value*='Complete Pledge']"))
    verify_cc_button.click()
    
    # verify that we are at pledge_complete
    # sleep a bit to give enough time for redirecto pledge_complete to finish
    
    time.sleep(3)
    
    # should be back on a pledge complete page
    print sel.current_url, re.search(r"/pledge/complete",sel.current_url)
    
    # need to pick out the actual work pledged.
    work_url = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector('p.pledge_complete a[href*="/work/"]'))
    work_url.click()

    # change_pledge
    print "clicking Modify Pledge button"
    change_pledge_button = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector("input[value*='Modify Pledge']"))
    change_pledge_button.click()
    
    # enter a new pledge, which is less than the previous amount 
    print "changing pledge to $5 -- should not need to go to Stripe"
    sel.execute_script("""document.getElementById("id_preapproval_amount").value="5";""")
    
    pledge_button = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector("input[value*='Modify Pledge']"))
    pledge_button.click()
    
    # return to the Work page again
    work_url = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector('p.pledge_complete a[href*="/work/"]'))
    work_url.click()
    change_pledge_button = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector("input[value*='Modify Pledge']"))
    change_pledge_button.click()
    
    # modify pledge to $25
    sel.execute_script("""document.getElementById("id_preapproval_amount").value="25";""")
    
    pledge_button = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector("input[value*='Modify Pledge']"))
    pledge_button.click()
    
    # now cancel transaction
    # now go back to the work page, hit modify pledge, and then the cancel link
    
    work_url = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector('p.pledge_complete a[href*="/work/"]'))
    work_url.click()
    change_pledge_button = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector("input[value*='Modify Pledge']"))
    change_pledge_button.click()
    cancel_url = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector('a[href*="/pledge/cancel"]'))
    cancel_url.click()
    
    # hit the confirm cancellation button
    cancel_pledge_button = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector("input[value*='Confirm Pledge Cancellation']"))
    cancel_pledge_button.click()    
    
    time.sleep(10)
    django.db.transaction.commit()
    
    yield sel

    # now use the transaction manager to make the charge
    w = models.Work.objects.get(id=48)
    c = w.campaigns.all()[0]
    pm = PaymentManager()
    result = pm.execute_campaign(c)
    
    # should have a Complete transaction
    print result
    
    yield sel
    


    
def successful_campaign_signal():
    """fire off a success_campaign signal and send notifications"""
    import regluit
    c = regluit.core.models.Campaign.objects.get(id=3)
    regluit.core.signals.successful_campaign.send(sender=None, campaign=c)
    

def berkeley_search():
    sel = selenium_driver(browser='firefox')
    sel.get("http://berkeley.edu")
    search = WebDriverWait(sel,5).until(lambda d: d.find_element_by_css_selector('input[id="search_text"]'))
    search.send_keys("quantum computing")
    
    return sel
    
    # wait for a bit and then highlight the text and fill it out with "Bach" instead
    # I was looking at using XPath natively in Firefox....
    # https://developer.mozilla.org/en/Introduction_to_using_XPath_in_JavaScript#Within_an_HTML_Document
    # document.evaluate('//input[@id="search_text"]', document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null ).snapshotItem(0); 
    
def suites():
    testcases = [GoogleWebDriverTest]
    suites = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(testcase) for testcase in testcases])
    

