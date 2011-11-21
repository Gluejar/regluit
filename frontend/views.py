import logging
from decimal import Decimal as D

from django.db.models import Q, Count
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
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response, get_object_or_404

import oauth2 as oauth
from itertools import islice

import re

from regluit.core import tasks
from regluit.core import models, bookloader, librarything
from regluit.core import userlists
from regluit.core.search import gluejar_search
from regluit.core.goodreads import GoodreadsClient
from regluit.frontend.forms import UserData, ProfileForm, CampaignPledgeForm, GoodreadsShelfLoadingForm
from regluit.frontend.forms import  RightsHolderForm, ClaimForm, LibraryThingForm, OpenCampaignForm
from regluit.frontend.forms import  ManageCampaignForm
from regluit.payment.manager import PaymentManager
from regluit.payment.parameters import TARGET_TYPE_CAMPAIGN

from regluit.core import goodreads
from tastypie.models import ApiKey

logger = logging.getLogger(__name__)

from regluit.payment.models import Transaction

import urllib
from re import sub

def home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('supporter',
            args=[request.user.username]))
    return render(request, 'home.html', {'suppress_search_box': True})

def stub(request):
    path = request.path[6:] # get rid of /stub/
    return render(request,'stub.html', {'path': path})

def work(request, work_id, action='display'):
    work = get_object_or_404(models.Work, id=work_id)
    campaign = work.last_campaign()

    claimform = ClaimForm(data={'work':work_id, 'user':request.user.id })
    if campaign:
        q = Q(campaign=campaign) | Q(campaign__isnull=True)
        premiums = models.Premium.objects.filter(q)
    else:
        premiums = None
    
    #may want to deprecate the following
    if action == 'setup_campaign':
        return render(request, 'setup_campaign.html', {'work': work})
    else:
        return render(request, 'work.html', {
            'work': work, 
            'premiums': premiums, 
            'ungluers': userlists.supporting_users(work, 5), 
            'claimform': claimform,
        })

def manage_campaign(request, id):
    campaign = get_object_or_404(models.Campaign, id=id)
    form= ManageCampaignForm(instance=campaign)
    return render(request, 'manage_campaign.html', {'campaign': campaign, 'form':form})
        
def workstub(request, title, imagebase, image, author, googlebooks_id, action='display'):
    premiums = None
    title = urllib.unquote_plus(title)
    imagebase = urllib.unquote_plus(imagebase)
    image = urllib.unquote_plus(image)
    author = urllib.unquote_plus(author)
    return render(request, 'workstub.html', {'title': title, 'image': image, 'imagebase': imagebase, 'author': author, 'googlebooks_id': googlebooks_id, 'premiums': premiums, 'ungluers': userlists.other_users(supporter, 5)})

def subjects(request):
    order = request.GET.get('order')
    subjects = models.Subject.objects.all()
    subjects = subjects.annotate(Count('editions'))

    if request.GET.get('order') == 'count':
        subjects = subjects.order_by('-editions__count')
    else:
        subjects = subjects.order_by('name')

    return render(request, 'subjects.html', {'subjects': subjects})

def pledge(request,work_id):
    work = get_object_or_404(models.Work, id=work_id)
    campaign = work.last_campaign()
    if campaign:
        premiums = campaign.premiums.all()
        if premiums.count() == 0:
            premiums = models.Premium.objects.filter(campaign__isnull=True)
    premium_id = request.GET.get('premium_id', None)
    if premium_id is not None:
        preapproval_amount = D(models.Premium.objects.get(id=premium_id).amount)
    else:
        preapproval_amount = D('0.00')
    data = {'preapproval_amount':preapproval_amount}
    form = CampaignPledgeForm(data)

    return render(request,'pledge.html',{'work':work,'campaign':campaign, 'premiums':premiums, 'form':form})

def claim(request):
    if  request.method == 'GET': 
        data = request.GET
    else:
        data =  request.POST
    form =  ClaimForm(data=data)
    if form.is_valid():
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
                    claim.campaign_form.save()
                    claim.can_open_new=False
            else:
                claim.campaign_form = OpenCampaignForm(data={'work': claim.work, 'name': claim.work.title, 'userid': request.user.id})
        else:
            claim.can_open_new=False
    return render(request, "rh_tools.html", {'claims': claims ,}) 

def rh_admin(request):
    if not request.user.is_authenticated() :
        return render(request, "admins_only.html")
    if not request.user.is_staff() :
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

    # figure out what works the users have in commmon if someone
    # is looking at someone else's supporter page
    if not request.user.is_anonymous and request.user != supporter:
        w1 = request.user.wishlist
        w2 = supporter.wishlist
        shared_works = models.Work.objects.filter(wishlists__in=[w1])
        shared_works = list(shared_works.filter(wishlists__in=[w2]))
    else: 
        shared_works = []

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
            "shared_works": shared_works,
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
        result['urlimage'] = urllib.quote_plus(sub('^https?:\/\/','', result['image']).encode("utf-8"), safe='')
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
        preapproval_amount = form.cleaned_data["preapproval_amount"]
        anonymous = form.cleaned_data["anonymous"]
        
        # right now, if there is a non-zero pledge amount, go with that.  otherwise, do the pre_approval
        campaign = models.Campaign.objects.get(id=int(pk))
        
        p = PaymentManager()
                    
        # we should force login at this point -- or if no account, account creation, login, and return to this spot
        if self.request.user.is_authenticated():
            user = self.request.user
        else:
            user = None
            
        # calculate the work corresponding to the campaign id
        work_id = campaign.work.id
        return_url = self.request.build_absolute_uri(reverse('work',kwargs={'work_id': str(work_id)}))
        t, url = p.authorize('USD', TARGET_TYPE_CAMPAIGN, preapproval_amount, campaign=campaign, list=None, user=user,
                            return_url=return_url, anonymous=anonymous)    
 
        #else:
        #    # instant payment:  send to the partnering RH
        #    # right now, all money going to Gluejar.  
        #    receiver_list = [{'email':settings.PAYPAL_GLUEJAR_EMAIL, 'amount':pledge_amount}]
        #    
        #    # redirect the page back to campaign page on success
        #    #return_url = self.request.build_absolute_uri("/campaigns/%s" %(str(pk)))
        #    return_url = self.request.build_absolute_uri(reverse('campaign_by_id',kwargs={'pk': str(pk)}))
        #    t, url = p.pledge('USD', TARGET_TYPE_CAMPAIGN, receiver_list, campaign=campaign, list=None, user=user,
        #                      return_url=return_url, anonymous=anonymous)
        
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
