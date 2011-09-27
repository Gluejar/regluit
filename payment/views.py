from regluit.payment.manager import PaymentManager
from regluit.payment.paypal import IPN
from regluit.payment.models import Transaction
from regluit.core.models import Campaign, Wishlist
from django.contrib.auth.models import User
from regluit.payment.parameters import *
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
import traceback

def queryCampaign(request):
    
    id = request.GET['id']
    campaign = Campaign.objects.get(id=id)
    
    p = PaymentManager()
    
    transactions = p.query_campaign(campaign)
    
    total = p.query_campaign(campaign, summary=True)
    
    return HttpResponse(str(total))
    
def testPledge(request):
    
    p = PaymentManager()
    
    if 'campaign' in request.GET.keys():
        campaign_id = request.GET['campaign']
    else:
        campaign_id = None
        
    
    # Note, set this to 1-5 different receivers with absolute amounts for each
    receiver_list = [{'email':'jakace_1309677337_biz@gmail.com', 'amount':20.00}, 
                     {'email':'boogus@gmail.com', 'amount':10.00}]
    
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
    
    
@csrf_exempt
def paypalIPN(request):
    # Handler for paypal IPN notifications
    
    p = PaymentManager()
    p.processIPN(request)
    
    print str(request.POST)
    return HttpResponse("ipn")
    