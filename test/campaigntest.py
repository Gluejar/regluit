from regluit.core import models
from regluit.payment.models import Transaction, PaymentResponse, Receiver
from regluit.payment.manager import PaymentManager
from regluit.payment.paypal import IPN_PREAPPROVAL_STATUS_ACTIVE, IPN_PAY_STATUS_INCOMPLETE, IPN_PAY_STATUS_COMPLETED

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


def support_campaign(unglue_it_url = settings.LIVE_SERVER_TEST_URL, do_local=True, backend='amazon'):
    """
    programatically fire up selenium to make a Pledge
    do_local should be True only if you are running support_campaign on db tied to LIVE_SERVER_TEST_URL
    """
    import django
    django.db.transaction.enter_transaction_management()
    
    UNGLUE_IT_URL = unglue_it_url
    # unglue.it login info
    USER = settings.UNGLUEIT_TEST_USER
    PASSWORD = settings.UNGLUEIT_TEST_PASSWORD
    
    # PayPal developer sandbox
    from regluit.payment.tests import loginSandbox, paySandbox, payAmazonSandbox
    
    setup_selenium()
    
    # we can experiment with different webdrivers
    sel = webdriver.Firefox()
    
    # Chrome
    #sel = webdriver.Chrome(executable_path='/Users/raymondyee/C/src/Gluejar/regluit/test/chromedriver')
    
    # HTMLUNIT with JS -- not successful
    #sel = webdriver.Remote("http://localhost:4444/wd/hub", webdriver.DesiredCapabilities.HTMLUNITWITHJS)

    time.sleep(10)
    
    # find a campaign to pledge to
    if backend == 'paypal':
        loginSandbox(sel)
        time.sleep(2)
        
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
    sel.find_element_by_css_selector("input[value*='sign in']").click()
    
    # click on biggest campaign list
    biggest_campaign_link = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector("a[href*='/campaigns/pledged']"))
    biggest_campaign_link.click()
    time.sleep(1)
    
    # pull up one of the campaigns to pledge to
    # for now, take the first book and click on the link to get to the work page
    work_links = WebDriverWait(sel,10).until(lambda d: d.find_elements_by_css_selector("div.book-list div.title a"))
    work_links[0].click()
    
    support_button = WebDriverWait(sel,10).until(lambda d: d.find_element_by_css_selector("input[value*='Support']"))
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

    # fill out a premium -- the first one for now
    premium_button = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector('input[type="radio"][value="1"]'))
    premium_button.click()
    
    # now we have to replace the current preapproval amount with 10
    sel.execute_script("""document.getElementById("id_preapproval_amount").value="10";""")
    
    ## enter a $10 pledge -- entering the pledge after clicking on premium is needed because clicking on premium fills in pledge amount
    #preapproval_amount_input = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector("input#id_preapproval_amount"))
    #preapproval_amount_input.send_keys("10")
    
    print "making $10 pledge"
    
    pledge_button = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector("input[value*='Pledge']"))
    pledge_button.click()
    
    # grab the URL where sel is now?
    
    if backend == 'paypal':
        print  "Now trying to pay PayPal", sel.current_url
        paySandbox(None, sel, sel.current_url, authorize=True, already_at_url=True, sleep_time=5)
    elif backend == 'amazon':
        payAmazonSandbox(sel)
    
        
    # should be back on a pledge complete page
    print sel.current_url, re.search(r"/pledge/complete",sel.current_url)
    
    time.sleep(2)
    django.db.transaction.commit()

    # time out to simulate an IPN -- update all the transactions
    if do_local:
        django.db.transaction.enter_transaction_management()
        pm = PaymentManager()
        print pm.checkStatus()
        transaction0 = Transaction.objects.all()[0]
        print "transaction amount:{0}, transaction premium:{1}".format(transaction0.amount, transaction0.premium.id)        
        django.db.transaction.commit()
        
    
    django.db.transaction.enter_transaction_management()

    # I have no idea what the a[href*="/work/"] is not displayed....so that's why I'm going up one element.
    work_url = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector('p > a[href*="/work/"]'))
    work_url.click()
    
    # change_pledge
    print "clicking Modify Pledge button"
    change_pledge_button = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector("input[value*='Modify Pledge']"))
    change_pledge_button.click()
    
    # enter a new pledge, which is less than the previous amount and therefore doesn't require a new PayPal transaction
    print "changing pledge to $5 -- should not need to go to PayPal"
    preapproval_amount_input = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector("input#id_preapproval_amount"))
    preapproval_amount_input.clear()  # get rid of existing pledge
    preapproval_amount_input.send_keys("5")
    pledge_button = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector("input[value*='Modify Pledge']"))
    pledge_button.click()
    
    # return to the Work page again
    work_url = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector('p > a[href*="/work/"]'))
    work_url.click()
    change_pledge_button = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector("input[value*='Modify Pledge']"))
    change_pledge_button.click()

    # enter a new pledge, which is more than the previous amount and therefore requires a new PayPal transaction
    preapproval_amount_input = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector("input#id_preapproval_amount"))
    preapproval_amount_input.clear()  # get rid of existing pledge
    preapproval_amount_input.send_keys("25")
    pledge_button = WebDriverWait(sel,20).until(lambda d: d.find_element_by_css_selector("input[value*='Modify Pledge']"))
    pledge_button.click()
    if backend == 'paypal':
        paySandbox(None, sel, sel.current_url, authorize=True, already_at_url=True, sleep_time=5)
    elif backend == 'amazon':
        payAmazonSandbox(sel)    

    # wait a bit to allow PayPal sandbox to be update the status of the Transaction    
    time.sleep(10)

    # Why is the status of the new transaction not being updated?
    
    django.db.transaction.commit()
    
    # force a db lookup -- see whether there are 1 or 2 transactions
    if do_local:
        transactions = list(Transaction.objects.all())
        print "number of transactions", Transaction.objects.count()
        
        print "transactions before pm.checkStatus"
        print [(t.id, t.type, t.preapproval_key, t.status, t.premium, t.amount) for t in Transaction.objects.all()]
    
        print "checkStatus:", pm.checkStatus(transactions=transactions)


    yield sel
    #sel.quit()
    
def successful_campaign_signal():
    """fire off a success_campaign signal and send notifications"""
    import regluit
    from notification.engine import send_all
    c = regluit.core.models.Campaign.objects.get(id=3)
    regluit.core.signals.successful_campaign.send(sender=None, campaign=c)
    send_all()
    

def berkeley_search():
    sel = webdriver.Firefox()
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
    

