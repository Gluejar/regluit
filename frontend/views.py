import logging
from decimal import Decimal as D

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.forms import Select
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response, get_object_or_404

import oauth2 as oauth
from itertools import islice

from regluit.core import tasks
from regluit.core import models, bookloader
from regluit.core.search import gluejar_search
from regluit.core.goodreads import GoodreadsClient
from regluit.frontend.forms import UserData, ProfileForm, CampaignPledgeForm, GoodreadsShelfLoadingForm
from regluit.payment.manager import PaymentManager
from regluit.payment.parameters import TARGET_TYPE_CAMPAIGN

from regluit.core import goodreads

logger = logging.getLogger(__name__)

from regluit.payment.models import Transaction

def home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('supporter',
            args=[request.user.username]))
    return render(request, 'home.html', {'suppress_search_box': True})

def work(request, work_id):
    work = get_object_or_404(models.Work, id=work_id)
    editions = work.editions.all().order_by('-publication_date')
    supporters = User.objects.filter(wishlist__works__in=[work])
    if not request.user.is_anonymous:
        supporters.remove(request.user)
    return render(request, 'work.html', {
        'work': work, 
        'editions': editions, 
        'supporters': supporters
    })

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

    # following block to support profile admin form in supporter page
    if request.user.is_authenticated() and request.user.username == supporter_username:
        if  request.method == 'POST': 
            try:
                profile_obj=request.user.get_profile()
            except ObjectDoesNotExist:
                profile_obj= models.UserProfile()
                profile_obj.user=request.user
            profile_form = ProfileForm(data=request.POST,instance=profile_obj)
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
        # add related editions asynchronously
        tasks.add_related.delay(edition.isbn_10)
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


class GoodreadsDisplayView(TemplateView):
    template_name = "goodreads_display.html"
    def get_context_data(self, **kwargs):
        context = super(GoodreadsDisplayView, self).get_context_data(**kwargs)
        session = self.request.session
        gr_client = GoodreadsClient(key=settings.GOODREADS_API_KEY, secret=settings.GOODREADS_API_SECRET)
        
        user = self.request.user

        if user.profile.goodreads_user_id is None:   
            # calculate the Goodreads authorization URL
            (context["goodreads_auth_url"], request_token) = gr_client.begin_authorization(self.request.build_absolute_uri(reverse('goodreads_cb')))
            logger.info("goodreads_auth_url: %s" %(context["goodreads_auth_url"]))
            # store request token in session so that we can redeem it for auth_token if authorization works
            session['goodreads_request_token'] = request_token['oauth_token']
            session['goodreads_request_secret'] = request_token['oauth_token_secret']
        else:
            gr_shelves = gr_client.shelves_list(user_id=user.profile.goodreads_user_id)
            context["shelves_info"] = gr_shelves
            gr_shelf_load_form = GoodreadsShelfLoadingForm()
            # load the shelves into the form
            choices = [('all','all (%d)' % (gr_shelves["total_book_count"]))] + [(s["name"],"%s (%d)" % (s["name"],s["book_count"])) for s in gr_shelves["user_shelves"]]
            gr_shelf_load_form.fields['goodreads_shelf_name'].widget = Select(choices=tuple(choices))
            
            context["gr_shelf_load_form"] = gr_shelf_load_form
            #context["reviews"] = list(islice(gr_client.review_list(user_id=user.profile.goodreads_user_id, per_page=50),50))
  
        return context

@login_required    
def goodreads_cb(request):
    """handle callback from Goodreads"""
    
    session = request.session
    authorized_flag = request.GET['authorize']  # is it '1'?
    request_oauth_token = request.GET['oauth_token']

    if authorized_flag == '1':
        request_token = {'oauth_token': session.get('goodreads_request_token'),
                         'oauth_token_secret': session.get('goodreads_request_secret')}
        gr_client = GoodreadsClient(key=settings.GOODREADS_API_KEY, secret=settings.GOODREADS_API_SECRET)
        
        access_token = gr_client.complete_authorization(request_token)
        
        # store the access token in the user profile
        profile = request.user.profile
        profile.goodreads_auth_token = access_token["oauth_token"]
        profile.goodreads_auth_secret = access_token["oauth_token_secret"]
    
        # let's get the userid, username
        user = gr_client.auth_user()
        
        profile.goodreads_user_id = user["userid"]
        profile.goodreads_user_name = user["name"]
        profile.goodreads_user_link = user["link"]
        
        profile.save()  # is this needed?

    # redirect to the Goodreads display page -- should observe some next later
    return HttpResponseRedirect(reverse('goodreads_display'))

@require_POST
@login_required
@csrf_exempt    
def goodreads_flush_assoc(request):
    user = request.user
    if user.is_authenticated():
        profile = user.profile
        profile.goodreads_user_id = None
        profile.goodreads_user_name = None
        profile.goodreads_user_link = None
        profile.goodreads_auth_token = None
        profile.goodreads_auth_secret = None
        profile.save()
    return HttpResponseRedirect(reverse('goodreads_display'))
      
@require_POST
@login_required      
@csrf_exempt
def goodreads_load_shelf(request):
    """
    a view to allow user load goodreads shelf into her wishlist
    """
    # Should be moved to the API
    goodreads_shelf_name = request.POST.get('goodreads_shelf_name', 'all')
    user = request.user
    try:
        logger.info('Adding task to load shelf %s to user %s', goodreads_shelf_name, user)
        tasks.load_goodreads_shelf_into_wishlist.delay(user, goodreads_shelf_name)
        return HttpResponse("Shelf loading placed on task queue.")
    except Exception,e:
        return HttpResponse("Error in loading shelf: %s " % (e))
        logger.info("Error in loading shelf: %s ", e)

@require_POST
@login_required      
@csrf_exempt        
def clear_wishlist(request):
    request.user.wishlist.clear()   
    