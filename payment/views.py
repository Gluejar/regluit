from regluit.payment.manager import PaymentManager
from regluit.payment.models import Transaction
from regluit.core.models import Campaign, Wishlist

from regluit.payment.stripelib import STRIPE_PK
from regluit.payment.forms import StripePledgeForm

from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.contrib.sites.models import RequestSite
from regluit.payment.parameters import *
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.test.utils import setup_test_environment
from django.template import RequestContext

from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView

from unittest import TestResult
from regluit.payment.tests import PledgeTest, AuthorizeTest
import uuid
from decimal import Decimal as D

from regluit.utils.localdatetime import now
import traceback


import logging
logger = logging.getLogger(__name__)

# parameterize some test recipients
TEST_RECEIVERS = ['seller_1317463643_biz@gmail.com', 'buyer5_1325740224_per@gmail.com']
#TEST_RECEIVERS = ['seller_1317463643_biz@gmail.com', 'Buyer6_1325742408_per@gmail.com']
#TEST_RECEIVERS = ['glueja_1317336101_biz@gluejar.com', 'rh1_1317336251_biz@gluejar.com', 'RH2_1317336302_biz@gluejar.com']


'''
http://BASE/querycampaign?id=2

Example that returns a summary total for a campaign
'''
def queryCampaign(request):
    
    id = request.GET['id']
    campaign = Campaign.objects.get(id=id)
    
    p = PaymentManager()
    
    # transactions = p.query_campaign(campaign)
    
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
            logger.info(str(t))
            
    else:
        transactions = Transaction.objects.filter(status=TRANSACTION_STATUS_ACTIVE)
        
        for t in transactions:
            
            # Note, set this to 1-5 different receivers with absolute amounts for each
            receiver_list = [{'email':TEST_RECEIVERS[0], 'amount':float(t.amount) * 0.80}, 
                            {'email':TEST_RECEIVERS[1], 'amount':float(t.amount) * 0.20}]
    
            p.execute_transaction(t, receiver_list)
            output += str(t)
            logger.info(str(t))
        
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
    receiver_list = [{'email': TEST_RECEIVERS[0], 'amount':20.00}, 
                     {'email': TEST_RECEIVERS[1], 'amount':10.00}]
        
    if campaign_id:
        campaign = Campaign.objects.get(id=int(campaign_id))
        t, url = p.authorize('USD', TARGET_TYPE_CAMPAIGN, amount, campaign=campaign, return_url=None, list=None, user=None)
    
    else:
        t, url = p.authorize('USD', TARGET_TYPE_NONE, amount, campaign=None, return_url=None, list=None, user=None)
    
    if url:
        logger.info("testAuthorize: " + url)
        return HttpResponseRedirect(url)
    
    else:
        response = t.error
        logger.info("testAuthorize: Error " + str(t.error))
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
    if p.cancel_transaction(t):
        return HttpResponse("Success")
    else:
        message = "Error: " + t.error
        return HttpResponse(message)
    
'''
http://BASE/testrefund?transaction=2

Example that refunds a transaction
'''    
def testRefund(request):
    
    if "transaction" not in request.GET.keys():
        return HttpResponse("No Transaction in Request")
    
    t = Transaction.objects.get(id=int(request.GET['transaction']))
    p = PaymentManager()
    if p.refund_transaction(t):
        return HttpResponse("Success")
    else:
        if t.error:
            message = "Error: " + t.error
        else:
            message = "Error"
            
        return HttpResponse(message)
    
'''
http://BASE/testmodify?transaction=2

Example that modifies the amount of a transaction
'''    
def testModify(request):
    
    if "transaction" not in request.GET.keys():
        return HttpResponse("No Transaction in Request")
    
    if "amount" in request.GET.keys():
        amount = float(request.GET['amount'])
    else:
        amount = 200.0
    
    t = Transaction.objects.get(id=int(request.GET['transaction']))
    p = PaymentManager()
        
    status, url = p.modify_transaction(t, amount, return_url=None)
    
    if url:
        logger.info("testModify: " + url)
        return HttpResponseRedirect(url)
    
    if status:
        return HttpResponse("Success")
    else:
        return HttpResponse("Error")
    
    
    
'''
http://BASE/testfinish?transaction=2

Example that finishes a delayed chained transaction
'''    
def testFinish(request):
    
    if "transaction" not in request.GET.keys():
        return HttpResponse("No Transaction in Request")
    
    t = Transaction.objects.get(id=int(request.GET['transaction']))
    p = PaymentManager()
    if p.finish_transaction(t):
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
    
    if 'campaign' in request.REQUEST.keys():
        campaign_id = request.REQUEST['campaign']
    else:
        campaign_id = None
        
    # see whether there is a user logged in.
    if request.user.is_authenticated():
        user = request.user
    else:
        user = None
    
    # Note, set this to 1-5 different receivers with absolute amounts for each
    #receiver_list = [{'email':TEST_RECEIVERS[0], 'amount':20.00},{'email':TEST_RECEIVERS[1], 'amount':10.00}]
    
    if 'pledge_amount' in request.REQUEST.keys():
        pledge_amount = request.REQUEST['pledge_amount']
        receiver_list = [{'email':TEST_RECEIVERS[0], 'amount':pledge_amount}]
    else:
        receiver_list = [{'email':TEST_RECEIVERS[0], 'amount':78.90}, {'email':TEST_RECEIVERS[1], 'amount':34.56}]
        
    if campaign_id:
        campaign = Campaign.objects.get(id=int(campaign_id))
        t, url = p.pledge('USD', TARGET_TYPE_CAMPAIGN, receiver_list, campaign=campaign, list=None, user=user, return_url=None)
    
    else:
        t, url = p.pledge('USD', TARGET_TYPE_NONE, receiver_list, campaign=None, list=None, user=user, return_url=None)
    
    if url:
        logger.info("testPledge: " + url)
        return HttpResponseRedirect(url)
    
    else:
        response = t.error
        logger.info("testPledge: Error " + str(t.error))
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
        logger.info(output)
    
        return HttpResponse(output)
    
    except:
        traceback.print_exc()
    
@csrf_exempt
def handleIPN(request, module):
    # Handler for paypal IPN notifications
    
    p = PaymentManager()
    p.processIPN(request, module)
    
    logger.info(str(request.POST))
    return HttpResponse("ipn")
    
    
def paymentcomplete(request):
    # pick up all get and post parameters and display
    output = "payment complete"
    output += request.method + "\n" + str(request.REQUEST.items())
    return HttpResponse(output)

def checkStatus(request):
    # Check the status of all PAY transactions and flag any errors
    p = PaymentManager()
    error_data = p.checkStatus()
        
    return HttpResponse(error_data, mimetype="text/xml")

# https://raw.github.com/agiliq/merchant/master/example/app/views.py

def _render(request, template, template_vars={}):
    return render_to_response(template, template_vars, RequestContext(request))
    
class StripeView(FormView):
    template_name="stripe.html"
    form_class = StripePledgeForm

    def get_context_data(self, **kwargs):
        
        context = super(StripeView, self).get_context_data(**kwargs)
    
        context.update({
                'STRIPE_PK':STRIPE_PK
                })
        return context
    
    def form_valid(self, form):
        stripeToken = form.cleaned_data["stripeToken"]
        # e.g., tok_0C0k4jG5B2Oxox
        # 
        return HttpResponse("stripeToken: {0}".format(stripeToken))
