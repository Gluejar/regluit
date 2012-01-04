from regluit.core import models
from regluit.payment.models import Transaction, PaymentResponse, Receiver
from regluit.payment.manager import PaymentManager
from regluit.payment.paypal import IPN_PAY_STATUS_ACTIVE, IPN_PAY_STATUS_INCOMPLETE, IPN_PAY_STATUS_COMPLETED

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
            sel.type("id=lst-ib", "Bach")
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

