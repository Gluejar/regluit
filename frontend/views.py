import re
import sys
import json
import urllib
import logging
import datetime 
from re import sub
from itertools import islice
from decimal import Decimal as D

import requests
import oauth2 as oauth
from django import forms
from django.db.models import Q, Count, Sum
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.forms import Select
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from regluit.core import tasks
from regluit.core import models, bookloader, librarything
from regluit.core import userlists
from regluit.core.search import gluejar_search
from regluit.core.goodreads import GoodreadsClient
from regluit.frontend.forms import UserData, ProfileForm, CampaignPledgeForm, GoodreadsShelfLoadingForm
from regluit.frontend.forms import  RightsHolderForm, UserClaimForm, LibraryThingForm, OpenCampaignForm
from regluit.frontend.forms import  ManageCampaignForm, DonateForm
from regluit.payment.manager import PaymentManager
from regluit.payment.parameters import TARGET_TYPE_CAMPAIGN, TARGET_TYPE_DONATION
from regluit.core import goodreads
from tastypie.models import ApiKey
from regluit.payment.models import Transaction


logger = logging.getLogger(__name__)


def home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('supporter',
            args=[request.user.username]))
    ending = models.Campaign.objects.filter(status='ACTIVE').order_by('deadline')
    j=0
    i=0
    works=[]
    works2=[]
    count=ending.count()
    while i<12 and count>0:
        if i<6:
            works.append(ending[j].work)
        else:
            works2.append(ending[j].work)
        i += 1
        j += 1
        if j == count:
            j = 0
    events = models.Wishes.objects.order_by('-created')[0:2]
    return render(request, 'home.html', {'suppress_search_box': True, 'works': works, 'works2': works2, 'events': events})

def stub(request):
    path = request.path[6:] # get rid of /stub/
    return render(request,'stub.html', {'path': path})

def work(request, work_id, action='display'):
    work = get_object_or_404(models.Work, id=work_id)
    editions = work.editions.all().order_by('-publication_date')
    campaign = work.last_campaign()
    
    if not request.user.is_anonymous():
        claimform = UserClaimForm( request.user, data={'work':work_id, 'user': request.user.id})
    else:
        claimform = None
    if campaign:
        q = Q(campaign=campaign) | Q(campaign__isnull=True)
        premiums = models.Premium.objects.filter(q)
    else:
        premiums = None
        
    wishers = work.wished_by().count()
    base_url = request.build_absolute_uri("/")[:-1]
    
    #may want to deprecate the following
    if action == 'setup_campaign':
        return render(request, 'setup_campaign.html', {'work': work})
    else:
        return render(request, 'work.html', {
            'work': work, 
            'premiums': premiums, 
            'ungluers': userlists.supporting_users(work, 5), 
            'claimform': claimform,
            'wishers': wishers,
            'base_url': base_url,
            'editions': editions,
        })

def manage_campaign(request, id):
    campaign = get_object_or_404(models.Campaign, id=id)
    campaign.not_manager=False
    campaign.problems=[]
    if (not request.user.is_authenticated) or (not request.user in campaign.managers.all()):
        campaign.not_manager=True
        return render(request, 'manage_campaign.html', {'campaign': campaign})
    alerts = []   
    if request.method == 'POST':
        form= ManageCampaignForm(instance=campaign, data=request.POST)  
        if form.is_valid():     
            form.save() 
            alerts.append(_('Campaign data has been saved'))
        else:
            alerts.append(_('Campaign data has NOT been saved'))
        if 'launch' in request.POST.keys():
            if campaign.launchable :
                campaign.activate()
                alerts.append(_('Campaign has been launched'))
            else:
                alerts.append(_('Campaign has NOT been launched'))
    else:
        form= ManageCampaignForm(instance=campaign)
    return render(request, 'manage_campaign.html', {'campaign': campaign, 'form':form, 'problems': campaign.problems, 'alerts': alerts})
        
def googlebooks(request, googlebooks_id):
    try: 
        edition = models.Edition.objects.get(googlebooks_id=googlebooks_id)
    except models.Edition.DoesNotExist:
        edition = bookloader.add_by_googlebooks_id(googlebooks_id)
        # we could populate_edition(edition) to pull in related editions here
        # but it is left out for now to lower the amount of traffic on 
        # googlebooks, librarything and openlibrary
    if not edition:
        return HttpResponseNotFound("invalid googlebooks id")
    work_url = reverse('work', kwargs={'work_id': edition.work.id})
    return HttpResponseRedirect(work_url)

def subjects(request):
    order = request.GET.get('order')
    subjects = models.Subject.objects.all()
    subjects = subjects.annotate(Count('works'))

    if request.GET.get('order') == 'count':
        subjects = subjects.order_by('-works__count')
    else:
        subjects = subjects.order_by('name')

    return render(request, 'subjects.html', {'subjects': subjects})


recommended_user = User.objects.filter( username=settings.UNGLUEIT_RECOMMENDED_USERNAME)

class WorkListView(ListView):
    template_name = "work_list.html"
    context_object_name = "work_list"
    
    def work_set_counts(self,work_set):
        counts={}
        counts['unglued'] = work_set.annotate(ebook_count=Count('editions__ebooks')).filter(ebook_count__gt=0).count()
        counts['unglueing'] = work_set.filter(campaigns__status='ACTIVE').count()
        counts['wished'] = work_set.count() - counts['unglued'] - counts['unglueing']
        return counts

    def get_queryset(self):
        facet = self.kwargs['facet']
        if (facet == 'popular'):
            return models.Work.objects.annotate(wished=Count('wishlists')).order_by('-wished')
        elif (facet == 'recommended'):
            return models.Work.objects.filter(wishlists__user=recommended_user)
        else:
            return models.Work.objects.all().order_by('-created')

    def get_context_data(self, **kwargs):
            context = super(WorkListView, self).get_context_data(**kwargs)
            qs=self.get_queryset()
            context['counts'] = self.work_set_counts(qs)
            context['ungluers'] = userlists.work_list_users(qs,5)
            context['facet'] =self.kwargs['facet']
            return context
        
class CampaignListView(ListView):
    template_name = "campaign_list.html"
    context_object_name = "campaign_list"
    model = models.Campaign

    def get_queryset(self):
        facet = self.kwargs['facet']
        if (facet == 'newest'):
            return models.Campaign.objects.filter(status='ACTIVE').order_by('-activated')
        elif (facet == 'pledged'):
            return models.Campaign.objects.filter(status='ACTIVE').annotate(total_pledge=Sum('transaction__amount')).order_by('-total_pledge')
        elif (facet == 'pledges'):
            return models.Campaign.objects.filter(status='ACTIVE').annotate(pledges=Count('transaction')).order_by('-pledges')
        elif (facet == 'almost'):
            return models.Campaign.objects.filter(status='ACTIVE').all() # STUB: will need to make db changes to make this work 
        elif (facet == 'ending'):
            return models.Campaign.objects.filter(status='ACTIVE').order_by('deadline')
        else:
            return models.Campaign.objects.all()

    def get_context_data(self, **kwargs):
            context = super(CampaignListView, self).get_context_data(**kwargs)
            qs=self.get_queryset()
            context['ungluers'] = userlists.campaign_list_users(qs,5)
            context['facet'] =self.kwargs['facet']
            return context
            
class PledgeView(FormView):
    template_name="pledge.html"
    form_class = CampaignPledgeForm
    embedded = False
    
    def get_context_data(self, **kwargs):
        context = super(PledgeView, self).get_context_data(**kwargs)
        
        work = get_object_or_404(models.Work, id=self.kwargs["work_id"])
        
        campaign = work.last_campaign()
        
        if campaign:
            premiums = campaign.effective_premiums()
                
        premium_id = self.request.REQUEST.get('premium_id', None)
        preapproval_amount = self.request.REQUEST.get('preapproval_amount', None)
        
        if premium_id is not None and preapproval_amount is None:
            try:
                preapproval_amount = D(models.Premium.objects.get(id=premium_id).amount)
            except:
                preapproval_amount = None
            
        logger.info("preapproval_amount, premium_id: %s %s ", preapproval_amount, premium_id)   
        data = {'preapproval_amount':preapproval_amount, 'premium_id':premium_id}
        
        form = CampaignPledgeForm(data)
    
        context.update({'work':work,'campaign':campaign, 'premiums':premiums, 'form':form, 'premium_id':premium_id})
        return context
    
    def form_valid(self, form):
        work_id = self.kwargs["work_id"]
        preapproval_amount = form.cleaned_data["preapproval_amount"]
        anonymous = form.cleaned_data["anonymous"]
        
        # right now, if there is a non-zero pledge amount, go with that.  otherwise, do the pre_approval
        campaign = models.Work.objects.get(id=int(work_id)).last_campaign()
        
        p = PaymentManager(embedded=self.embedded)
                    
        # we should force login at this point -- or if no account, account creation, login, and return to this spot
        if self.request.user.is_authenticated():
            user = self.request.user
        else:
            user = None
                   
        if not self.embedded:
            
            return_url = self.request.build_absolute_uri(reverse('work',kwargs={'work_id': str(work_id)}))
            # the recipients of this authorization is not specified here but rather by the PaymentManager.
            t, url = p.authorize('USD', TARGET_TYPE_CAMPAIGN, preapproval_amount, campaign=campaign, list=None, user=user,
                            return_url=return_url, anonymous=anonymous)    
        else:  # embedded view -- which we're not actively using right now.
            # embedded view triggerws instant payment:  send to the partnering RH
            receiver_list = [{'email':settings.PAYPAL_NONPROFIT_PARTNER_EMAIL, 'amount':preapproval_amount}]
            
            #redirect the page back to campaign page on success
            return_url = self.request.build_absolute_uri(reverse('campaign_by_id',kwargs={'pk': str(pk)}))
            t, url = p.pledge('USD', TARGET_TYPE_CAMPAIGN, receiver_list, campaign=campaign, list=None, user=user,
                              return_url=return_url, anonymous=anonymous)
        
        if url:
            logger.info("PledgeView paypal: " + url)
            print >> sys.stderr, "CampaignFormView paypal: ", url
            return HttpResponseRedirect(url)
        else:
            response = t.reference
            logger.info("PledgeView paypal: Error " + str(t.reference))
            return HttpResponse(response)
    
class DonateView(FormView):
    template_name="donate.html"
    form_class = DonateForm
    embedded = False
    
    #def get_context_data(self, **kwargs):
    #    context = super(DonateView, self).get_context_data(**kwargs)
    #    
    #    form = CampaignPledgeForm(data)
    #
    #    context.update({'work':work,'campaign':campaign, 'premiums':premiums, 'form':form, 'premium_id':premium_id})
    #    return context
    
    def form_valid(self, form):
        donation_amount = form.cleaned_data["donation_amount"]
        anonymous = form.cleaned_data["anonymous"]
        
        # right now, if there is a non-zero pledge amount, go with that.  otherwise, do the pre_approval
        campaign = None
        
        p = PaymentManager(embedded=self.embedded)
                    
        # we should force login at this point -- or if no account, account creation, login, and return to this spot
        if self.request.user.is_authenticated():
            user = self.request.user
        else:
            user = None

        # instant payment:  send to the partnering RH
        receiver_list = [{'email':settings.PAYPAL_NONPROFIT_PARTNER_EMAIL, 'amount':donation_amount}]
        
        #redirect the page back to campaign page on success
        return_url = self.request.build_absolute_uri(reverse('donate'))
        
        t, url = p.pledge('USD', TARGET_TYPE_DONATION, receiver_list, campaign=campaign, list=None, user=user,
                          return_url=return_url, anonymous=anonymous)
    
        if url:
            return HttpResponseRedirect(url)
        else:
            response = t.reference
            logger.info("PledgeView paypal: Error " + str(t.reference))
            return HttpResponse(response)
    
    
def claim(request):
    if  request.method == 'GET': 
        data = request.GET
    else:
        data =  request.POST
    form =  UserClaimForm(request.user, data=data)
    if form.is_valid():
        # make sure we're not creating a duplicate claim
        if not models.Claim.objects.filter(work=data['work'], rights_holder=data['rights_holder'], status='pending').count():
            form.save()
        return HttpResponseRedirect(reverse('work', kwargs={'work_id': data['work']}))
    else:
        work = models.Work.objects.get(id=data['work'])
        rights_holder = models.RightsHolder.objects.get(id=data['rights_holder'])
        context = {'form': form, 'work': work, 'rights_holder':rights_holder }
        return render(request, "claim.html", context)

def rh_tools(request):
    if not request.user.is_authenticated() :
        return render(request, "rh_tools.html")
    claims = request.user.claim.filter(user=request.user)
    campaign_form = "xxx"
    if not claims:
        return render(request, "rh_tools.html")
    for claim in claims:
        claim.campaigns= claim.work.campaigns.all()
        claim.can_open_new=True
        for campaign in claim.campaigns:
            if campaign.status in ['ACTIVE','INITIALIZED']:
                claim.can_open_new=False
        if claim.status == 'active' and claim.can_open_new:
            if request.method == 'POST' and int(request.POST['work']) == claim.work.id :
                claim.campaign_form = OpenCampaignForm(request.POST)
                if claim.campaign_form.is_valid():                    
                    new_campaign = claim.campaign_form.save(commit=False)
                    new_campaign.deadline = datetime.date.today() + datetime.timedelta(days=int(settings.UNGLUEIT_LONGEST_DEADLINE))
                    new_campaign.target = D(settings.UNGLUEIT_MINIMUM_TARGET)
                    new_campaign.save()
                    claim.campaign_form.save_m2m()
                    claim.can_open_new=False
            else:
                claim.campaign_form = OpenCampaignForm(data={'work': claim.work, 'name': claim.work.title, 'userid': request.user.id})
        else:
            claim.can_open_new=False
    return render(request, "rh_tools.html", {'claims': claims ,}) 

def rh_admin(request):
    if not request.user.is_authenticated() :
        return render(request, "admins_only.html")
    if not request.user.is_staff :
        return render(request, "admins_only.html")
    PendingFormSet = modelformset_factory(models.Claim, fields=['status'], extra=0)
    pending_data = models.Claim.objects.filter(status = 'pending')
    active_data = models.Claim.objects.filter(status = 'active')
    if  request.method == 'POST': 
        if 'create_rights_holder' in request.POST.keys():
            form = RightsHolderForm(data=request.POST)
            pending_formset = PendingFormSet (queryset=pending_data)
            if form.is_valid():
                form.save()
        if 'set_claim_status' in request.POST.keys():
            pending_formset = PendingFormSet (request.POST, request.FILES, queryset=pending_data)
            form = RightsHolderForm()
            if pending_formset.is_valid():
                pending_formset.save()
                pending_formset = PendingFormSet(queryset=pending_data)
    else:
        form = RightsHolderForm()
        pending_formset = PendingFormSet(queryset=pending_data)
    rights_holders = models.RightsHolder.objects.all()
    
    context = { 
        'request': request, 
        'rights_holders': rights_holders, 
        'form': form,
        'pending': zip(pending_data,pending_formset),
        'pending_formset': pending_formset,
        'active_data': active_data,
    }
    return render(request, "rights_holders.html", context)


def supporter(request, supporter_username, template_name):
    supporter = get_object_or_404(User, username=supporter_username)
    wishlist = supporter.wishlist
    works = wishlist.works.all()
    backed = 0
    backing = 0
    transet = Transaction.objects.all().filter(user = supporter)
    
    for transaction in transet:
        try:
            if(transaction.campaign.status == 'SUCCESSFUL'):
                backed += 1
            elif(transaction.campaign.status == 'ACTIVE'):
                backing += 1
        except:
            continue
            
    wished = supporter.wishlist.works.count()
    
    date = supporter.date_joined.strftime("%B %d, %Y")

    # following block to support profile admin form in supporter page
    if request.user.is_authenticated() and request.user.username == supporter_username:

        try:
            profile_obj=request.user.get_profile()
        except ObjectDoesNotExist:
            profile_obj= models.UserProfile()
            profile_obj.user=request.user

        if  request.method == 'POST': 
            profile_form = ProfileForm(data=request.POST,instance=profile_obj)
            if profile_form.is_valid():
                if profile_form.cleaned_data['clear_facebook'] or profile_form.cleaned_data['clear_twitter'] :
                    if profile_form.cleaned_data['clear_facebook']:
                        profile_obj.facebook_id=0
                    if profile_form.cleaned_data['clear_twitter']:
                        profile_obj.twitter_id=""
                    profile_obj.save()
                profile_form.save()

        else:
            profile_form= ProfileForm(instance=profile_obj)
            
        # for now, also calculate the Goodreads shelves of user when loading this page
        # we should move towards calculating this only if needed (perhaps with Ajax), caching previous results, etc to speed up
        # performance
        
        if request.user.profile.goodreads_user_id is not None:
            gr_client = GoodreadsClient(key=settings.GOODREADS_API_KEY, secret=settings.GOODREADS_API_SECRET)
            goodreads_shelves = gr_client.shelves_list(user_id=request.user.profile.goodreads_user_id)
            goodreads_shelf_load_form = GoodreadsShelfLoadingForm()
            # load the shelves into the form
            choices = [('all:%d' % (goodreads_shelves["total_book_count"]),'all (%d)' % (goodreads_shelves["total_book_count"]))] +  \
                [("%s:%d" % (s["name"], s["book_count"]) ,"%s (%d)" % (s["name"],s["book_count"])) for s in goodreads_shelves["user_shelves"]]
            goodreads_shelf_load_form.fields['goodreads_shelf_name_number'].widget = Select(choices=tuple(choices))
        else:
            goodreads_shelf_load_form = None                        

        if request.user.profile.librarything_id is not None:
            librarything_id = request.user.profile.librarything_id
        else:
            librarything_id = None
    else:
        profile_form = ''
        goodreads_shelf_load_form = None
        librarything_id = None

        
    context = {
            "supporter": supporter,
            "wishlist": wishlist,
            "works": works,
            "backed": backed,
            "backing": backing,
            "wished": wished,
            "date": date,
            "profile_form": profile_form,
            "ungluers": userlists.other_users(supporter, 5 ),
            "goodreads_auth_url": reverse('goodreads_auth'),
            "goodreads_shelf_load_form": goodreads_shelf_load_form,
            "librarything_id": librarything_id
    }
    
    return render(request, template_name, context)

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
    results = gluejar_search(q, request.META['REMOTE_ADDR'])

    # flag search result as on wishlist as appropriate
    if not request.user.is_anonymous():
        # get a list of all the googlebooks_ids for works on the user's wishlist
        wishlist = request.user.wishlist
        editions = models.Edition.objects.filter(work__wishlists__in=[wishlist])
        googlebooks_ids = [e['googlebooks_id'] for e in editions.values('googlebooks_id')]
        ungluers = userlists.other_users(request.user, 5)
        # if the results is on their wishlist flag it
        for result in results:
            if result['googlebooks_id'] in googlebooks_ids:
                result['on_wishlist'] = True
            else:
                result['on_wishlist'] = False
    else:
        ungluers = userlists.other_users(None, 5)
            
    # also urlencode some parameters we'll need to pass to workstub in the title links
    # needs to be done outside the if condition
    for result in results:
        result['urlimage'] = urllib.quote_plus(sub('^https?:\/\/','', result['cover_image_thumbnail']).encode("utf-8"), safe='')
        result['urlauthor'] = urllib.quote_plus(result['author'].encode("utf-8"), safe='')
        result['urltitle'] = urllib.quote_plus(result['title'].encode("utf-8"), safe='')

    context = {
        "q": q,
        "results": results,
        "ungluers": ungluers
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
        tasks.populate_edition.delay(edition)
        request.user.wishlist.add_work(edition.work,'user')
        # TODO: redirect to work page, when it exists
        return HttpResponseRedirect('/')
    elif remove_work_id:
        work = models.Work.objects.get(id=int(remove_work_id))
        request.user.wishlist.remove_work(work)
        # TODO: where to redirect?
        return HttpResponseRedirect('/')
  
class CampaignFormView(FormView):
    template_name="campaign_detail.html"
    form_class = CampaignPledgeForm
    embedded = False
    
    def get_context_data(self, **kwargs):
        pk = self.kwargs["pk"]
        campaign = models.Campaign.objects.get(id=int(pk))
        context = super(CampaignFormView, self).get_context_data(**kwargs)
        base_url = self.request.build_absolute_uri("/")[:-1]
        context.update({
           'embedded': self.embedded,
           'campaign': campaign,
           'base_url':base_url
        })
        
        return context

    def form_valid(self,form):
        pk = self.kwargs["pk"]
        preapproval_amount = form.cleaned_data["preapproval_amount"]
        anonymous = form.cleaned_data["anonymous"]
        
        # right now, if there is a non-zero pledge amount, go with that.  otherwise, do the pre_approval
        campaign = models.Campaign.objects.get(id=int(pk))
        
        p = PaymentManager(embedded=self.embedded)
                    
        # we should force login at this point -- or if no account, account creation, login, and return to this spot
        if self.request.user.is_authenticated():
            user = self.request.user
        else:
            user = None
            
        # calculate the work corresponding to the campaign id
        work_id = campaign.work.id
        
        if not self.embedded:
            
            return_url = self.request.build_absolute_uri(reverse('work',kwargs={'work_id': str(work_id)}))
            t, url = p.authorize('USD', TARGET_TYPE_CAMPAIGN, preapproval_amount, campaign=campaign, list=None, user=user,
                            return_url=return_url, anonymous=anonymous)    
        else:
            # instant payment:  send to the partnering RH
            # right now, all money going to Gluejar.  
            receiver_list = [{'email':settings.PAYPAL_GLUEJAR_EMAIL, 'amount':preapproval_amount}]
            
            #redirect the page back to campaign page on success
            return_url = self.request.build_absolute_uri(reverse('campaign_by_id',kwargs={'pk': str(pk)}))
            t, url = p.pledge('USD', TARGET_TYPE_CAMPAIGN, receiver_list, campaign=campaign, list=None, user=user,
                              return_url=return_url, anonymous=anonymous)
        
        if url:
            logger.info("CampaignFormView paypal: " + url)
            print >> sys.stderr, "CampaignFormView paypal: ", url
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
        if user.is_authenticated():
            api_key = ApiKey.objects.filter(user=user)[0].key
            context['api_key'] = api_key

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
            choices = [('all:%d' % (gr_shelves["total_book_count"]),'all (%d)' % (gr_shelves["total_book_count"]))] +  \
                [("%s:%d" % (s["name"], s["book_count"]) ,"%s (%d)" % (s["name"],s["book_count"])) for s in gr_shelves["user_shelves"]]
            gr_shelf_load_form.fields['goodreads_shelf_name_number'].widget = Select(choices=tuple(choices))
            
            context["gr_shelf_load_form"] = gr_shelf_load_form
            
# also load any CeleryTasks associated with the user
            context["celerytasks"] = models.CeleryTask.objects.filter(user=user)
            
        return context

@login_required
def goodreads_auth(request):

    # calculate the Goodreads authorization URL
    gr_client = GoodreadsClient(key=settings.GOODREADS_API_KEY, secret=settings.GOODREADS_API_SECRET)
    (goodreads_auth_url, request_token) = gr_client.begin_authorization(request.build_absolute_uri(reverse('goodreads_cb')))
    logger.info("goodreads_auth_url: %s" %(goodreads_auth_url))
    # store request token in session so that we can redeem it for auth_token if authorization works
    request.session['goodreads_request_token'] = request_token['oauth_token']
    request.session['goodreads_request_secret'] = request_token['oauth_token_secret']
    
    return HttpResponseRedirect(goodreads_auth_url)

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
    return HttpResponseRedirect(reverse('home'))

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
        logger.info('Goodreads association flushed for user %s', user)
    return HttpResponseRedirect(reverse('goodreads_display'))
      
@require_POST
@login_required      
@csrf_exempt
def goodreads_load_shelf(request):
    """
    a view to allow user load goodreads shelf into her wishlist
    """
    # Should be moved to the API
    goodreads_shelf_name_number = request.POST.get('goodreads_shelf_name_number', 'all:0')
    user = request.user
    try:
        # parse out shelf name and expected number of books
        (shelf_name, expected_number_of_books) = re.match(r'^(.*):(\d+)$', goodreads_shelf_name_number).groups()
        expected_number_of_books = int(expected_number_of_books)
        logger.info('Adding task to load shelf %s to user %s with %d books', shelf_name, user, expected_number_of_books)
        load_task_name = "load_goodreads_shelf_into_wishlist"
        load_task = getattr(tasks, load_task_name)
        task_id = load_task.delay(user, shelf_name, expected_number_of_books=expected_number_of_books)
        
        ct = models.CeleryTask()
        ct.task_id = task_id
        ct.function_name = load_task_name
        ct.user = user
        ct.description = "Loading Goodread shelf %s to user %s with %s books" % (shelf_name, user, expected_number_of_books)
        ct.save()
        
        return HttpResponse("Shelf loading placed on task queue.")
    except Exception,e:
        return HttpResponse("Error in loading shelf: %s " % (e))
        logger.info("Error in loading shelf for user %s: %s ", user, e)


@require_POST
@login_required      
@csrf_exempt
def librarything_load(request):
    """
    a view to allow user load librarything library into her wishlist
    """
    # Should be moved to the API
    user = request.user

    
    try:        
        # figure out expected_number_of_books later
        
        lt_username = request.user.profile.librarything_id
        logger.info('Adding task to load librarything %s to user %s', lt_username, user )
        load_task_name = "load_librarything_into_wishlist"
        load_task = getattr(tasks, load_task_name)
        task_id = load_task.delay(user, lt_username, None)
        
        ct = models.CeleryTask()
        ct.task_id = task_id
        ct.function_name = load_task_name
        ct.user = user
        ct.description = "Loading LibraryThing collection of %s to user %s." % (lt_username, user)
        ct.save()
        
        return HttpResponse("LibraryThing loading placed on task queue.")
    except Exception,e:
        return HttpResponse("Error in loading LibraryThing library: %s " % (e))
        logger.info("Error in loading LibraryThing for user %s: %s ", user, e)

@require_POST
@login_required      
@csrf_exempt
def clear_wishlist(request):
    try:
        request.user.wishlist.works.clear()
        logger.info("Wishlist for user %s cleared", request.user)
        return HttpResponse('wishlist cleared')
    except Exception, e:
        return HttpResponse("Error in clearing wishlist: %s " % (e))
        logger.info("Error in clearing wishlist for user %s: %s ", request.user, e)
    

class LibraryThingView(FormView):
    template_name="librarything.html"
    form_class = LibraryThingForm
    
    def get_context_data(self, **kwargs):
        context = super(LibraryThingView, self).get_context_data(**kwargs)
        form = kwargs['form']
        # get the books for the lt_username in the form
        lt_username=self.request.GET.get("lt_username",None)
        if lt_username is not None:
            lt = librarything.LibraryThing(username=lt_username)
            context.update({'books':list(lt.parse_user_catalog(view_style=5))})
        else:
            context.update({'books':None})
            
        # try picking up the LibraryThing api key -- and set to None if not available.  Not being used for
        # anything crucial at this moment, so a None is ok here
        try:
            context.update({'lt_api_key':settings.LIBRARYTHING_API_KEY})
        except:
            pass
        
        return context

    def form_valid(self,form):
        return super(LibraryThingView, self).form_valid(form)
    
@require_POST
@login_required      
@csrf_exempt
def clear_celery_tasks(request):
    try:
        request.user.tasks.clear()
        logger.info("Celery tasks for user %s cleared", request.user)
        return HttpResponse('Celery Tasks List cleared')
    except Exception, e:
        return HttpResponse("Error in clearing Celery Tasks: %s " % (e))
        logger.info("Error in clearing Celery Tasks for user %s: %s ", request.user, e)    

def celery_test(request):
    return HttpResponse("celery_test")

# routing views that try to redirect to the works page on a 3rd party site
#
# TODO: need to queue up a task to look up IDs if we have to fallback to 
# routing based on ISBN or search

def work_librarything(request, work_id):
    work = get_object_or_404(models.Work, id=work_id)
    isbn = work.first_isbn_10()
    if work.librarything_id:
        url = work.librarything_url
    elif isbn:
        # TODO: do the redirect here and capture the work id?
        url = "http://www.librarything.com/isbn/%s" % work.first_isbn_10()
    else:
        term = work.title + " " + work.author()
        q = urllib.urlencode({'searchtpe': 'work', 'term': term})
        url = "http://www.librarything.com/search.php?" + q
    return HttpResponseRedirect(url)

def work_openlibrary(request, work_id):
    work = get_object_or_404(models.Work, id=work_id)
    isbns = ["ISBN:" + e.isbn_10 for e in work.editions.filter(isbn_10__isnull=False)]
    url = None

    if work.openlibrary_id:
        url = work.openlibrary_url
    elif len(isbns) > 0:
        isbns = ",".join(isbns)
        u = 'http://openlibrary.org/api/books?bibkeys=%s&jscmd=data&format=json' % isbns
        j = json.loads(requests.get(u).content)
        # as long as there were some matches get the first one and route to it
        if len(j.keys()) > 0:
            first = j.keys()[0]
            url = "http://openlibrary.org" + j[first]['key'] 
    # fall back to doing a search on openlibrary
    if not url:
        q = urllib.urlencode({'q': work.title + " " + work.author()})
        url = "http://openlibrary.org/search?" + q
    return HttpResponseRedirect(url)

def work_goodreads(request, work_id):
    work = get_object_or_404(models.Work, id=work_id)
    isbn = work.first_isbn_10()
    if work.goodreads_id:
        url = work.goodreads_url
    elif isbn:
        url = "http://www.goodreads.com/book/isbn/%s" % work.first_isbn_10()
    else:
        q = urllib.urlencode({'query': work.title + " " + work.author()})
        url = "http://www.goodreads.com/search?" + q
    return HttpResponseRedirect(url)
