from regluit.payment.manager import PaymentManager
from regluit.payment.paypal import IPN
from regluit.payment.models import Transaction
from regluit.core.models import Campaign, Wishlist
from django.contrib.auth.models import User
from regluit.payment.parameters import *
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.test.utils import setup_test_environment
from unittest import TestResult
from regluit.payment.tests import PledgeTest, AuthorizeTest
import traceback

'''
http://BASE/querycampaign?id=2

Example that returns a summary total for a campaign
'''
def queryCampaign(request):
    
    id = request.GET['id']
    campaign = Campaign.objects.get(id=id)
    
    p = PaymentManager()
    
    transactions = p.query_campaign(campaign)
    
    total = p.query_campaign(campaign, summary=True)
    
    return HttpResponse(str(total))

'''
http://BASE/testexecute?campaign=2

Example that executes a set of transactions that are pre-approved
'''
def testExecute(request):
    
    p = PaymentManager()
    
    if 'campaign' in request.GET.keys():
        campaign_id = request.GET['campaign']
        campaign = Campaign.objects.get(id=int(campaign_id))
    else:
        campaign = None
        
    output = ''
        
    if campaign:
        result = p.execute_campaign(campaign)
        
        for t in result:
            output += str(t)
            print str(t)
            
    else:
        transactions = Transaction.objects.filter(status='ACTIVE')
        
        for t in transactions:
            
            # Note, set this to 1-5 different receivers with absolute amounts for each
            receiver_list = [{'email':'jakace_1309677337_biz@gmail.com', 'amount':t.amount * 0.80}, 
                            {'email':'seller_1317463643_biz@gmail.com', 'amount':t.amount * 0.20}]
    
            p.execute_transaction(t, receiver_list)
            output += str(t)
            print str(t)
        
    return HttpResponse(output)
        

'''
http://BASE/testauthorize?amount=20

Example that initiates a pre-approval for a set amount
'''   
def testAuthorize(request):
    
    p = PaymentManager()
    
    if 'campaign' in request.GET.keys():
        campaign_id = request.GET['campaign']
    else:
        campaign_id = None
        
    if 'amount' in request.GET.keys():
        amount = float(request.GET['amount'])
    else:
        return HttpResponse("Error, no amount in request")
        
    
    # Note, set this to 1-5 different receivers with absolute amounts for each
    receiver_list = [{'email':'jakace_1309677337_biz@gmail.com', 'amount':20.00}, 
                     {'email':'seller_1317463643_biz@gmail.com', 'amount':10.00}]
    
    if campaign_id:
        campaign = Campaign.objects.get(id=int(campaign_id))
        t, url = p.authorize('USD', TARGET_TYPE_CAMPAIGN, amount, campaign=campaign, list=None, user=None)
    
    else:
        t, url = p.authorize('USD', TARGET_TYPE_NONE, amount, campaign=None, list=None, user=None)
    
    if url:
        print "testAuthorize: " + url
        return HttpResponseRedirect(url)
    
    else:
        response = t.reference
        print "testAuthorize: Error " + str(t.reference)
        return HttpResponse(response)
 
'''
http://BASE/testcancel?transaction=2

Example that cancels a preapproved transaction
'''    
def testCancel(request):
    
    if "transaction" not in request.GET.keys():
        return HttpResponse("No Transaction in Request")
    
    t = Transaction.objects.get(id=int(request.GET['transaction']))
    p = PaymentManager()
    if p.cancel(t):
        return HttpResponse("Success")
    else:
        message = "Error: " + t.error
        return HttpResponse(message)

    
'''
http://BASE/testpledge?campaign=2

Example that initiates an instant payment for a campaign
'''    
def testPledge(request):
    
    p = PaymentManager()
    
    if 'campaign' in request.GET.keys():
        campaign_id = request.GET['campaign']
    else:
        campaign_id = None
        
    
    # Note, set this to 1-5 different receivers with absolute amounts for each
    receiver_list = [{'email':'rh1_1317336251_biz@gluejar.com', 'amount':20.00},]
    
    if campaign_id:
        campaign = Campaign.objects.get(id=int(campaign_id))
        t, url = p.pledge('USD', TARGET_TYPE_CAMPAIGN, receiver_list, campaign=campaign, list=None, user=None)
    
    else:
        t, url = p.pledge('USD', TARGET_TYPE_NONE, receiver_list, campaign=None, list=None, user=None)
    
    if url:
        print "testPledge: " + url
        return HttpResponseRedirect(url)
    
    else:
        response = t.reference
        print "testPledge: Error " + str(t.reference)
        return HttpResponse(response)

def runTests(request):

    try:
        # Setup the test environement.  We need to run these tests on a live server
        # so our code can receive IPN notifications from paypal
        setup_test_environment()
        result = TestResult()
        
        # Run the authorize test
        test = AuthorizeTest('test_authorize')
        test.run(result)   
    
        # Run the pledge test
        test = PledgeTest('test_pledge_single_receiver')
        test.run(result)
        
        # Run the pledge failure test
        test = PledgeTest('test_pledge_too_much')
        test.run(result)

        output = "Tests Run: " + str(result.testsRun) + str(result.errors) + str(result.failures)
        print output
    
        return HttpResponse(output)
    
    except:
        traceback.print_exc()
    
@csrf_exempt
def paypalIPN(request):
    # Handler for paypal IPN notifications
    
    p = PaymentManager()
    p.processIPN(request)
    
    print str(request.POST)
    return HttpResponse("ipn")
    
