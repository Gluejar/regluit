from django.template import RequestContext
from django.contrib.auth.models import User
# from django.contrib.auth.forms import UserChangeForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response, get_object_or_404

from django.conf import settings

from regluit.core import models, bookloader
from regluit.core.search import gluejar_search

from regluit.frontend.forms import UserData,ProfileForm
from regluit.frontend.forms import CampaignPledgeForm

from regluit.payment.manager import PaymentManager
from regluit.payment.parameters import TARGET_TYPE_CAMPAIGN

from decimal import Decimal as D

import logging
logger = logging.getLogger(__name__)

from regluit.payment.models import Transaction

def home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('supporter',
            args=[request.user.username]))
    return render(request, 'home.html', {'suppress_search_box': True})

def supporter(request, supporter_username):
    supporter = get_object_or_404(User, username=supporter_username)
    wishlist = supporter.wishlist
    backed = 0
    backing = 0
    transet = Transaction.objects.all().filter(user = supporter)
    
    for transaction in transet:
        if(transaction.campaign.status == 'SUCCESSFUL'):
            backed += 1
        elif(transaction.campaign.status == 'ACTIVE'):
            backing += 1
            
    wished = supporter.wishlist.works.count()
    
    date = supporter.date_joined.strftime("%B %d, %Y")

    # figure out what works the users have in commmon if someone
    # is looking at someone elses supporter page
    if not request.user.is_anonymous and request.user != supporter:
        w1 = request.user.wishlist
        w2 = supporter.wishlist
        shared_works = models.Work.objects.filter(wishlists__in=[w1])
        shared_works = list(shared_works.filter(wishlists__in=[w2]))
    else: 
        shared_works = []

    # added following blok to support profile admin form in supporter page
    if request.user.is_authenticated() and request.user.username == supporter_username:
        if  request.method == 'POST': 
            profile_form = ProfileForm(data=request.POST,instance=request.user.get_profile())
            if profile_form.is_valid():
                profile_form.save()
        else:
            profile_form = ProfileForm()
    else:
        profile_form = ''
            
    context = {
            "supporter": supporter,
            "wishlist": wishlist,
            "backed": backed,
            "backing": backing,
            "wished": wished,
            "date": date,
            "shared_works": shared_works,
            "profile_form": profile_form,
    }
    
    return render(request, 'supporter.html', context)

def edit_user(request):
    form=UserData()
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('auth_login'))
    oldusername=request.user.username
    if request.method == 'POST': 
        # surely there's a better way to add data to the POST data?
        postcopy=request.POST.copy()
        postcopy['oldusername']=oldusername 
        form = UserData(postcopy)
        if form.is_valid(): # All validation rules pass, go and change the username
            request.user.username=form.cleaned_data['username']
            request.user.save()
            return HttpResponseRedirect(reverse('home')) # Redirect after POST
    return render(request,'registration/user_change_form.html', {'form': form},)  


def search(request):
    q = request.GET.get('q', None)
    results = gluejar_search(q)

    # flag search result as on wishlist as appropriate
    if not request.user.is_anonymous():
        # get a list of all the googlebooks_ids for works on the user's wishlist
        wishlist = request.user.wishlist
        editions = models.Edition.objects.filter(work__wishlists__in=[wishlist])
        googlebooks_ids = [e['googlebooks_id'] for e in editions.values('googlebooks_id')]

        # if the results is on their wishlist flag it
        for result in results:
            if result['googlebooks_id'] in googlebooks_ids:
                result['on_wishlist'] = True
            else:
                result['on_wishlist'] = False

    context = {
        "q": q,
        "results": results,
    }
    return render(request, 'search.html', context)

# TODO: perhaps this functionality belongs in the API?
@require_POST
@login_required
@csrf_exempt
def wishlist(request):
    googlebooks_id = request.POST.get('googlebooks_id', None)
    remove_work_id = request.POST.get('remove_work_id', None)
    if googlebooks_id:
        edition = bookloader.add_by_googlebooks_id(googlebooks_id)
        request.user.wishlist.works.add(edition.work)
        # TODO: redirect to work page, when it exists
        return HttpResponseRedirect('/')
    elif remove_work_id:
        work = models.Work.objects.get(id=int(remove_work_id))
        request.user.wishlist.works.remove(work)
        # TODO: where to redirect?
        return HttpResponseRedirect('/')
  
class CampaignFormView(FormView):
    template_name="campaign_detail.html"
    form_class = CampaignPledgeForm
    
    def get_context_data(self, **kwargs):
        pk = self.kwargs["pk"]
        campaign = models.Campaign.objects.get(id=int(pk))
        context = super(CampaignFormView, self).get_context_data(**kwargs)
        context.update({
           'campaign': campaign
        })
        return context
    def form_valid(self,form):
        pk = self.kwargs["pk"]
        pledge_amount = form.cleaned_data["pledge_amount"]
        preapproval_amount = form.cleaned_data["preapproval_amount"]
        
        # right now, if there is a non-zero pledge amount, go with that.  otherwise, do the pre_approval
        campaign = models.Campaign.objects.get(id=int(pk))
        
        p = PaymentManager()
                    
        # we should force login at this point -- or if no account, account creation, login, and return to this spot
        if self.request.user.is_authenticated():
            user = self.request.user
        else:
            user = None
 
        if (preapproval_amount > D('0.00')):
            # handle preapproval: get preapproval to charge amount of money in preapproval_amount
            
            return_url = self.request.build_absolute_uri(reverse('campaign_by_id',kwargs={'pk': str(pk)}))
            t, url = p.authorize('USD', TARGET_TYPE_CAMPAIGN, preapproval_amount, campaign=campaign, list=None, user=user,
                                 return_url=return_url)    
        else:
            # instant payment:  send to the partnering RH
            # right now, all money going to Gluejar.  
            receiver_list = [{'email':settings.PAYPAL_GLUEJAR_EMAIL, 'amount':pledge_amount}]
            
            # redirect the page back to campaign page on success
            #return_url = self.request.build_absolute_uri("/campaigns/%s" %(str(pk)))
            return_url = self.request.build_absolute_uri(reverse('campaign_by_id',kwargs={'pk': str(pk)}))
            t, url = p.pledge('USD', TARGET_TYPE_CAMPAIGN, receiver_list, campaign=campaign, list=None, user=user,
                              return_url=return_url)
        
        if url:
            logger.info("CampaignFormView paypal: " + url)
            return HttpResponseRedirect(url)
        else:
            response = t.reference
            logger.info("CampaignFormView paypal: Error " + str(t.reference))
            return HttpResponse(response)
