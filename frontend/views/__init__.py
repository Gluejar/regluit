'''
external library imports
'''
import functools
import re
import sys
import json
import logging
from urllib.parse import unquote
import requests

from datetime import timedelta, date, datetime
from decimal import Decimal as D
from itertools import chain
from notification import models as notification
from random import randint
from tastypie.models import ApiKey

#django imports

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import redirect_to_login
from django_comments.models import Comment
from django.contrib.sites.models import Site
from django.core import signing
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.mail import EmailMessage
from django.urls import reverse, reverse_lazy
from django.core.validators import validate_email
from django.db.models import Q, Count, Sum
from django.db.utils import IntegrityError
from django.forms import Select
from django.forms.models import inlineformset_factory
from django.http import (
    HttpResponseRedirect,
    Http404,
    HttpResponse,
    HttpResponseNotFound
)
from django.shortcuts import render, get_object_or_404
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.views.generic.base import (
    TemplateView,
)

#regluit imports

from regluit.core import (
    tasks,
    models,
    bookloader,
    librarything,
    userlists,
)
import regluit.core.cc as cc
from regluit.core.bookloader import merge_works, detach_editions
from regluit.core.isbn import ISBN
from regluit.core.search import gluejar_search
from regluit.core.signals import supporter_message
from regluit.core.tasks import send_mail_task, watermark_acq
from regluit.core.parameters import *
from regluit.core.facets import get_facet_object, get_order_by

from regluit.frontend.forms import (
    ProfileForm,
    CampaignPledgeForm,
    CampaignPurchaseForm,
    CampaignThanksForm,
    RightsHolderForm,
    UserClaimForm,
    LibraryThingForm,
    CampaignAdminForm,
    EmailShareForm,
    FeedbackForm,
    EbookForm,
    EbookFileForm,
    PledgeCancelForm,
    getTransferCreditForm,
    CCForm,
    AnonCCForm,
    AccountCCForm,
    CloneCampaignForm,
    PlainCCForm,
    WorkForm,
    OtherWorkForm,
    MsgForm,
    PressForm,
    KindleEmailForm,
    LibModeForm,
    DateCalculatorForm,
    RegiftForm,
    SubjectSelectForm,
    MapSubjectForm,
    DonationForm,
)

from regluit.payment import baseprocessor, stripelib
from regluit.payment.credit import credit_transaction
from regluit.payment.manager import PaymentManager
from regluit.payment.models import Transaction, CreditLog
from regluit.payment.parameters import (
    TRANSACTION_STATUS_ACTIVE,
    TRANSACTION_STATUS_COMPLETE,
    TRANSACTION_STATUS_CANCELED,
    TRANSACTION_STATUS_INCOMPLETE,
    TRANSACTION_STATUS_NONE,
    TRANSACTION_STATUS_MODIFIED,
    PAYMENT_TYPE_AUTHORIZATION,
    PAYMENT_HOST_NONE,
    COMPANY_TITLE
)

from regluit.libraryauth.forms import UserNamePass
from regluit.libraryauth.views import Authenticator, superlogin, login_user
from regluit.libraryauth.models import Library
from regluit.marc.views import qs_marc_records
from regluit.utils.localdatetime import date_today

from .bibedit import edit_edition, user_can_edit_work, safe_get_work, get_edition
from .rh_views import campaign_results, claim, manage_campaign, rh_admin, RHAgree, rh_tools
from . import cf

logger = logging.getLogger(__name__)

def log_time(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        page = method(*args, **kwargs)
        end_time = datetime.now()
        logging.debug('returned %s. Total time: %s' % (method, (end_time - start_time)))
        return page
    return wrapper    
    

def static_redirect_view(request, file_name, dir=""):
    return HttpResponseRedirect('/static/'+dir+"/"+file_name)

def slideshow():
    max = 8
    ending = models.Campaign.objects.filter(status='ACTIVE').order_by('deadline')
    count = ending.count()
    j = 0

    worklist = []
    if max > count:
        # add all the works with active campaigns
        for campaign in ending:
            worklist.append(campaign.work)

        # then fill out the rest of the list with slide works
        remainder = max - count
        remainder_works = models.Work.objects.filter(campaigns__status="SUCCESSFUL").order_by('-campaigns__deadline')[:remainder]
        worklist.extend(remainder_works)
    else:
        # if the active campaign list has more works than we can fit
        # in our slideshow, it's the only source we need to draw from
        while j < max:
            worklist.append(ending[j].work)
            j += 1

    return (worklist[:4], worklist[4:8])

def process_kindle_email(request):
    """
    check for kindle_email in session in case this is a redirect after
    download + login/account creation; add kindle email to profile
    """
    user = request.user
    if user.is_authenticated and 'kindle_email' in request.session:
        user.profile.kindle_email = request.session['kindle_email']
        user.profile.save()
        request.session.pop('kindle_email')

def next(request):
    if 'next' in request.COOKIES:
        response = HttpResponseRedirect(unquote(unquote(request.COOKIES['next'])))
        response.delete_cookie('next')
        return response
    else:
        return HttpResponseRedirect('/')

def cover_width(work):
    if work.percent_of_goal() < 100:
        cover_width = 100 - work.percent_of_goal()
    else:
        cover_width = 0

    return cover_width

@log_time
def home(request, landing=False):
    faves = None
    if request.user.is_authenticated :
        next = request.GET.get('next', False)
        if next:
            # should happen only for new users
            return HttpResponseRedirect(next)
        else:
            wishes = request.user.wishlist.wishes_set.all().order_by('-created')[:4]
            faves = [wish.work for wish in wishes]
    """
    use campaigns instead of works so that we can order by amount left,
    drive interest toward most-nearly-successful
    """
    try:
        featured = models.Work.objects.filter(featured__isnull=False).distinct().order_by('-featured')[0]
    except:
        #shouldn't occur except in tests
        featured = models.Work.objects.first()
    top_pledge = models.Campaign.objects.filter(status="ACTIVE", type=REWARDS).order_by('left')[:4]
    top_b2u = models.Campaign.objects.filter(status="ACTIVE", type=BUY2UNGLUE).order_by('-work__num_wishes')[:4]
    top_t4u = models.Campaign.objects.exclude(id = featured.id).filter(status="ACTIVE", type=THANKS).order_by('-work__num_wishes')[:4]

    most_wished = models.Work.objects.order_by('-num_wishes')[:4]

    unglued_books = models.Work.objects.filter(campaigns__status="SUCCESSFUL").order_by('-campaigns__deadline')[:4]

    cc_books = models.Work.objects.exclude(id = featured.id).filter(
                                          featured__isnull=False,
                                         ).distinct().order_by('-featured')[:4]

    """
    get various recent types of site activity
    """
    latest_comments = Comment.objects.order_by(
            '-submit_date'
        )[:10]
    latest_pledges = Transaction.objects.filter(
            anonymous=False, campaign__isnull=False
        ).exclude(
            type=0  #incomplete
        ).only(
            'date_created', 'user', 'campaign'
        ).order_by(
            '-date_created'
        )[:10]
    latest_wishes = models.Wishes.objects.filter(source='user').order_by(
            '-created'
        )[:10]

    """
    for each event, we'll be passing its object and type to the template
    (and preserving its date for sorting purposes)
    """
    latest_comments_tuple = map(
        lambda x: (x.submit_date, x, 'comment'),
        latest_comments
    )

    latest_pledges_tuple = map(
        lambda x: (x.date_created, x, 'pledge'),
        latest_pledges
    )

    latest_wishes_tuple = map(
        lambda x: (x.created, x, 'wish'),
        latest_wishes
    )

    """
    merge latest actions into a single list, sorted by date, to loop through in template
    """
    latest_actions = sorted(
        chain(latest_comments_tuple, latest_pledges_tuple, latest_wishes_tuple),
        key=lambda instance: instance[0],
        reverse=True
    )

    if request.user.is_authenticated:
        events = latest_actions[:12]
    else:
        events = latest_actions[:6]

    return render(
        request,
        'home.html',
        {
            'events': events,
            'top_pledge': top_pledge,
            'top_b2u': top_b2u,
            'top_t4u': top_t4u,
            'unglued_books': unglued_books,
            'cc_books': cc_books,
            'most_wished': most_wished,
            'featured': featured,
            'faves': faves,
        }
    )

def stub(request):
    path = request.path[6:] # get rid of /stub/
    return render(request, 'stub.html', {'path': path})

def acks(request, work):
    return render(request, 'front_matter.html', {'campaign': work.last_campaign()})

@log_time
def work(request, work_id, action='display'):
    work = safe_get_work(work_id)
    alert = ''
    if request.method == "HEAD":
        return render(request, 'worksummary.html', {'work': work,})
    formset = None
    if action == "acks":
        return acks(request, work)
    elif action == "editions":
        EditionFormSet = inlineformset_factory(models.Work, models.Edition, fields=(), extra=0)
        if request.method == "POST" and (request.user.is_staff or (work.last_campaign() and request.user in work.last_campaign().managers.all())):
            formset = EditionFormSet(data=request.POST, instance=work)
            if formset.is_valid():
                to_split = [form.instance for form in formset.deleted_forms]
                if to_split:
                    detach_editions(to_split)
                    alert = 'editions have been split'
            if 'select_edition' in request.POST:
                selected_id = request.POST['select_edition']
                try:
                    work.selected_edition = work.editions.get(id=selected_id)
                    work.title = work.selected_edition.title
                    work.save()
                    alert = alert + 'edition selected'
                except models.Edition.DoesNotExist:
                    pass
        formset = EditionFormSet(instance=work)

    # process waiting add request
    if not request.user.is_anonymous and "add_wishlist" in request.session:
        add_url = request.session["add_wishlist"]
        if add_url == request.path:
            request.user.wishlist.add_work(work, "login", notify=True)
            request.session.pop("add_wishlist")

    process_kindle_email(request)

    if request.method == 'POST' and not request.user.is_anonymous:
        activetab = '4'
    elif action == 'editions':
        activetab = '4'
    else:
        try:
            activetab = request.GET['tab']
            if activetab not in ['1', '2', '3', '4']:
                activetab = '1'
        except:
            activetab = '1'

    campaign = work.last_campaign()
    editions = work.editions.all().order_by('-publication_date')[:10]
    try:
        supported =  campaign.transactions().filter(user=request.user)
        pledged = supported.filter(status="ACTIVE")
    except:
        supported = None
        pledged = None

    cover_width_number = 0

    if work.last_campaign_status() == 'ACTIVE':
        cover_width_number = cover_width(work)

    if action == 'preview':
        work.last_campaign_status = 'ACTIVE'

    if not request.user.is_anonymous:
        claimform = UserClaimForm(request.user, initial={'work':work.pk, 'user': request.user.id}, prefix = 'claim')
    else:
        claimform = None

    if campaign:
        # pull up premiums explicitly tied to the campaign
        # mandatory premiums are only displayed in pledge process
        premiums = campaign.custom_premiums()
    else:
        premiums = None

    wishers = work.num_wishes
    base_url = request.build_absolute_uri("/")[:-1]

    active_claims = work.claim.all().filter(status='active')
    if active_claims.count() == 1:
        claimstatus = 'one_active'
        rights_holder_name = active_claims[0].rights_holder.rights_holder_name
    else:
        rights_holder_name = None
        pending_claims = work.claim.all().filter(status='pending')
        pending_claims_count = pending_claims.count()
        if pending_claims_count > 1:
            claimstatus = 'disputed'
        elif pending_claims_count == 1:
            claimstatus = 'one_pending'
            rights_holder_name = pending_claims[0].rights_holder.rights_holder_name
        else:
            claimstatus = 'open'

    return render(request, 'work.html', {
        'work': work,
        'user_can_edit_work': user_can_edit_work(request.user, work),
        'premiums': premiums,
        'claimform': claimform,
        'wishers': wishers,
        'base_url': base_url,
        'editions': editions,
        'pledged': pledged,
        'supported': supported,
        'activetab': activetab,
        'alert': alert,
        'claimstatus': claimstatus,
        'rights_holder_name': rights_holder_name,
        'cover_width': cover_width_number,
        'action': action,
        'formset': formset,
        'kwform': SubjectSelectForm()
    })

def edition_uploads(request, edition_id):
    context = {}
    if not request.user.is_authenticated:
        return render(request, "admins_only.html")
    edition = get_edition(edition_id)
    campaign_type = edition.work.last_campaign().type
    if not user_can_edit_work(request.user, edition.work):
        return render(request, "admins_only.html")
    if request.method == 'POST' :
        form = EbookFileForm(data=request.POST, files=request.FILES, campaign_type=campaign_type)
        if form.is_valid() :
            logger.info("EbookFileForm is_valid")
            form.save()
            edition.work.last_campaign().save()
            context['uploaded'] = True
            if campaign_type == BUY2UNGLUE:
                if edition.work.last_campaign().status == 'SUCCESSFUL':
                    try:
                        edition.work.last_campaign().watermark_success()
                    except Exception as e:
                        context['upload_error'] = e
                        form.instance.delete()
                else:
                    # campaign mangager gets a copy
                    test_acq = models.Acq.objects.create(user=request.user, work=edition.work, license= TESTING)
                    try:
                        test_acq.get_watermarked()
                        context['watermarked'] = test_acq.watermarked
                    except Exception as e:
                        context['upload_error'] = e
                        form.instance.delete()
            if campaign_type == THANKS:
                e = form.instance.check_file()
                if e != None:
                    logger.error(e)
                    context['upload_error'] = e
                    form.instance.delete()
                else:
                    tasks.process_ebfs.delay(edition.work.last_campaign().id)
                if form.instance.id:
                    new_ebook = models.Ebook.objects.create(
                        edition=edition,
                        format=form.instance.format,
                        url=form.instance.file.url,
                        rights=edition.work.last_campaign().license,
                        version_label=form.cleaned_data.get('version_label', ''),
                        active=False,
                        provider="Unglue.it",
                    )
                    form.instance.ebook = new_ebook
                    form.instance.ebook.set_next_iter()
                    form.instance.save()

        else:
            context['upload_error'] = form.errors
    form = EbookFileForm(initial={'edition':edition, 'format':'epub'}, campaign_type=campaign_type)
    context.update({
            'form': form, 'edition': edition,
            'ebook_files': models.EbookFile.objects.filter(edition = edition)
        })
    return render(request, 'edition_uploads.html', context)

@login_required
def manage_ebooks(request, edition_id, by=None):
    if edition_id:
        try:
            edition = models.Edition.objects.get(id = edition_id)
        except models.Edition.DoesNotExist:
            raise Http404
        work = edition.work
    else:
        raise Http404
    # if the work and edition are set, we save the edition and set the work

    alert = ''
    admin = user_can_edit_work(request.user, work)
    if request.method == 'POST' :
        ebook_form = EbookForm(data = request.POST, files=request.FILES,)
        if ebook_form.is_valid():
            if ebook_form.cleaned_data.get('file', None):
                file=ebook_form.cleaned_data['file']
                new_ebf = models.EbookFile.objects.create(
                    file=file,
                    format=ebook_form.cleaned_data['format'],
                    edition=edition,
                )
                ebook_form.instance.url = new_ebf.file.url
                ebook_form.instance.provider = "Unglue.it"
                ebook_form.instance.save()
                new_ebf.ebook = ebook_form.instance
                new_ebf.save()
                new_ebf.ebook.filesize = new_ebf.file.size
                new_ebf.ebook.save()                
            else:
                ebook_form.save()
                ebook_form.instance.set_next_iter()
            edition.work.remove_old_ebooks()
            alert = 'Thanks for adding an ebook to unglue.it!'
        else:
            alert = 'your submitted ebook had errors'
    else:
        ebook_form = EbookForm(instance=models.Ebook(user=request.user, edition=edition, provider='x'))
    try:
        show_ebook_form = admin or edition.work.last_campaign().status not in ['ACTIVE','INITIALIZED']
    except:
        show_ebook_form = True
    return render(request, 'manage_ebooks.html', {
            'edition': edition, 'admin':admin, 'alert':alert,
             'ebook_form': ebook_form, 'show_ebook_form':show_ebook_form,
        })


BAD_ROBOTS = [u'memoryBot']
def is_bad_robot(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    for robot in BAD_ROBOTS:
        try:
            if robot in user_agent:
                return True
        except UnicodeDecodeError:
            # user agent is sending illegal header
            return True
    return False        

def googlebooks(request, googlebooks_id):
    try:
        edition = models.Identifier.objects.get(type='goog', value=googlebooks_id).edition
    except models.Identifier.DoesNotExist:
        if is_bad_robot(request):
            return HttpResponseNotFound("failed looking up googlebooks id %s" % googlebooks_id)
        try:
            edition = bookloader.add_by_googlebooks_id(googlebooks_id)
            if edition and edition.new:
                # add related editions asynchronously
                tasks.populate_edition.delay(edition.isbn_13)
                if request.user.is_authenticated:
                    request.user.profile.works.add(edition.work)
        except bookloader.LookupFailure:
            logger.warning("failed to load googlebooks_id %s" % googlebooks_id)
            return HttpResponseNotFound("failed looking up googlebooks id %s" % googlebooks_id)
        except IntegrityError:
            logger.warning("duplicate (maybe) googlebooks_id %s" % googlebooks_id)
            return HttpResponseNotFound("failed adding googlebooks id %s" % googlebooks_id)
            
    if not edition:
        return HttpResponseNotFound("invalid googlebooks id")
    work_url = reverse('work', kwargs={'work_id': edition.work_id})

    # process waiting add request
    if not request.user.is_anonymous and "add_wishlist" in request.session:
        add_url = request.session["add_wishlist"]
        if add_url == request.path:
            request.user.wishlist.add_work(edition.work, "login", notify=True)
            request.session.pop("add_wishlist")

    return HttpResponseRedirect(work_url)

def subjects(request):
    order = request.GET.get('order')
    subjects = models.Subject.objects.all()
    subjects = subjects
    if request.GET.get('subset') == 'free':
        subjects = models.Subject.objects.filter(works__is_free = True).annotate(Count('works__is_free'))
        if request.GET.get('order') == 'count':
            subjects = subjects.order_by('-works__is_free__count')
        else:
            subjects = subjects.order_by('name')
    else:
        subjects = models.Subject.objects.all().annotate(Count('works'))
        if request.GET.get('order') == 'count':
            subjects = subjects.order_by('-works__count')
        else:
            subjects = subjects.order_by('name')

    return render(request, 'subjects.html', {'subjects': subjects})

class MapSubjectView(FormView):
    """
    Allows a staffer to add given subject to all works with given the onto_subject keyword.
    e.g., subject = "Language" onto_subject="English language"
    """
    template_name = "map_subject.html"
    form_class = MapSubjectForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return render(request, "admins_only.html")
        else:
            return super(MapSubjectView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        context = self.get_context_data()
        context['subject'] = form.cleaned_data['subject']
        context['onto_subject'] = form.cleaned_data['onto_subject']
        if 'confirm_map_subject' in self.request.POST:
            initial_count = context['onto_subject'].works.all().count()
            initial_free_count = context['onto_subject'].works.filter(is_free=True).count()
            context['onto_subject'].works.add(*list(context['subject'].works.all()))
            context['map_complete'] = True
            context['form'] = MapSubjectForm(initial=form.cleaned_data)
            context['added'] = context['onto_subject'].works.all().count() - initial_count
            context['added_free'] = context['onto_subject'].works.filter(is_free=True).count() - initial_free_count
        else:
            context['form'] = MapSubjectForm(initial=form.cleaned_data)
        return render(self.request, self.template_name, context)

class FilterableListView(ListView):
    send_marc = False
    def get_queryset(self):
        if 'pub_lang' in self.request.GET:
            if self.model is models.Campaign:
                return self.get_queryset_all().filter(work__language=self.request.GET['pub_lang'])
            else:
                return self.get_queryset_all().filter(language=self.request.GET['pub_lang'])
        else:
            return self.get_queryset_all()

    def get_context_data(self, **kwargs):
        context = super(FilterableListView, self).get_context_data(**kwargs)
        if 'pub_lang' in self.request.GET:
            context['pub_lang'] = self.request.GET['pub_lang']
        else:
            context['pub_lang'] = ''
        context['show_langs'] = True
        context['WISHED_LANGS'] = settings.WISHED_LANGS
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.send_marc:
            return qs_marc_records(self.request, qs=self.object_list)
        else:
            return super(FilterableListView, self).render_to_response(context, **response_kwargs)

recommended_user = User.objects.filter(username=settings.UNGLUEIT_RECOMMENDED_USERNAME)

class WorkListView(FilterableListView):
    template_name = "work_list.html"
    context_object_name = "work_list"

    def get_queryset_all(self):
        facet = self.kwargs.get('facet', None)
        if facet == 'popular':
            return models.Work.objects.exclude(num_wishes=0).order_by('-num_wishes')
        elif facet == 'recommended':
            self.template_name = "recommended.html"
            return models.Work.objects.filter(wishlists__user=recommended_user).order_by('-num_wishes')
        else:
            return models.Work.objects.all().order_by('-created')

    def get_context_data(self, **kwargs):
        context = super(WorkListView, self).get_context_data(**kwargs)
        qs = self.get_queryset()
        context['facet'] = self.kwargs.get('facet','all')
        context['works_unglued'] = qs.filter(is_free=True).distinct()
        context['url_name'] = 'work_list_nopub'
        return context

class FacetedView(FilterableListView):
    template_name = "faceted_list.html"
    def get_queryset_all(self):
        if not hasattr(self,'vertex'):
            facet_path = self.kwargs.get('path', '')
            self.vertex = get_facet_object(facet_path)

        order_by = self.request.GET.get('order_by', 'newest')

        # robots occasionally mangle order_by
        order_by = order_by if order_by in ORDER_BY_KEYS else 'newest'

        #special cases
        if order_by == 'subjects':
            return self.vertex.get_query_set().annotate(kws=Count('subjects')).order_by('kws')
        return self.vertex.get_query_set().distinct().order_by(*get_order_by(order_by))

    def get_context_data(self, **kwargs):
        context = super(FacetedView, self).get_context_data(**kwargs)
        facet = self.kwargs.get('facet','all')
        qs = self.get_queryset()
        if 'setkw' in self.request.GET and self.request.user.is_staff:
            setkw = self.request.GET['setkw']
            try:
                context['setkw'] =  models.Subject.objects.get(name=setkw)
            except models.Subject.DoesNotExist:
                pass
        context['activetab'] = "#1"
        context['tab_override'] = 'tabs-1'
        context['path'] = self.vertex.get_facet_path().replace('//','/').strip('/')
        context['vertex'] = self.vertex

        order_by = self.request.GET.get('order_by', 'newest')        
        # robots occasionally mangle order_by
        context['order_by'] = order_by if order_by in ORDER_BY_KEYS else 'newest'

        context['view_as'] = self.request.GET.get('view_as', None)
        return context


class ByPubView(WorkListView):
    template_name = "bypub_list.html"
    context_object_name = "work_list"
    publisher_name = None
    publisher = None

    def get_publisher_name(self):
        try:
            self.publisher_name = get_object_or_404(models.PublisherName, id=self.kwargs['pubname'])
        except ValueError:
            raise Http404
        self.set_publisher()

    def set_publisher(self):
        if self.publisher_name.key_publisher.exists():
            self.publisher = self.publisher_name.key_publisher.first()
        elif self.publisher_name.publisher:
            self.publisher = self.publisher_name.publisher
            self.publisher_name = self.publisher.name

    def get_queryset_all(self):
        facet = self.kwargs.get('facet','')
        self.get_publisher_name()
        objects = models.Work.objects.filter(editions__publisher_name__id=self.publisher_name.id).distinct()
        if facet == 'popular':
            return objects.order_by('-num_wishes', 'id')
        elif facet == 'pubdate':
            return objects.order_by('-editions__publication_date') # turns out this messes up distinct, and MySQL doesn't support DISTINCT ON
        elif facet == 'new':
            return objects.filter(num_wishes__gt=0).order_by('-created', '-num_wishes' ,'id')
        else:
            return objects.order_by('title', 'id')

    def get_context_data(self, **kwargs):
        context = super(ByPubView, self).get_context_data(**kwargs)
        context['pubname'] = self.publisher_name
        context['publisher'] = self.publisher
        context['facet'] = self.kwargs.get('facet','all')
        context['url_name'] = 'bypub_list'

        return context

class ByPubListView(ByPubView):
    def get_publisher_name(self):
        self.publisher_name = get_object_or_404(models.PublisherName, name=self.kwargs['pubname'])
        self.set_publisher()


class UngluedListView(FilterableListView):
    template_name = "unglued_list.html"
    context_object_name = "work_list"

    def get_queryset_all(self):
        facet = self.kwargs['facet']
        if (facet == 'popular'):
            return models.Work.objects.filter(is_free = True).distinct().order_by('-num_wishes')
        elif (facet == 'cc' or facet == 'creativecommons'):
            # assumes all ebooks have a PD or CC license. compare rights_badge property
            return models.Work.objects.filter(
                                              is_free = True,
                                              editions__ebooks__rights__in=cc.LICENSE_LIST
                                             ).exclude(campaigns__status="SUCCESSFUL").distinct().order_by('-num_wishes')
        elif (facet == 'pd' or facet == 'publicdomain'):
            return models.Work.objects.filter(
                                              is_free = True,
                                              editions__ebooks__rights__in=['PD-US', 'CC0', '']
                                             ).distinct().order_by('-num_wishes')
        else :
            #(facet == '' or facet == 'unglued' or facet is other)
            return models.Work.objects.filter(campaigns__status="SUCCESSFUL").distinct().order_by('-campaigns__deadline')

    def get_context_data(self, **kwargs):
        context = super(UngluedListView, self).get_context_data(**kwargs)
        qs = self.get_queryset()
        facet = self.kwargs['facet']
        context['facet'] = facet
        if facet == 'cc' or facet == 'creativecommons':
            context['activetab'] = "#2"
        elif facet == 'pd' or facet == 'publicdomain':
            context['activetab'] = "#3"
        else:
            context['activetab'] = "#1"
        return context
FACET_LABELS = {
    'b2u': "Buy to Unglue",
    't4u': "Thanks for Ungluing",
    'pledge': "Pledge to Unglue",
    'unglued': "Successful",
}
class CampaignListView(FilterableListView):
    template_name = "campaign_list.html"
    context_object_name = "campaign_list"
    model = models.Campaign

    def get_queryset_all(self):
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
        elif (facet == 'soon'):
            return models.Campaign.objects.filter(status='INITIALIZED').order_by('-work__num_wishes')
        elif (facet == 'b2u'):
            return models.Campaign.objects.filter(status='ACTIVE', type=BUY2UNGLUE).annotate(pledges=Count('transaction')).order_by('-pledges')
        elif (facet == 't4u'):
            return models.Campaign.objects.filter(status='ACTIVE', type=THANKS).annotate(pledges=Count('transaction')).order_by('-pledges')
        elif (facet == 'pledge'):
            return models.Campaign.objects.filter(status='ACTIVE', type=REWARDS).annotate(pledges=Count('transaction')).order_by('-pledges')
        elif (facet == 'unglued'):
            return models.Campaign.objects.filter(status='SUCCESSFUL').annotate(pledges=Count('transaction')).order_by('-pledges')
        else:
            return models.Campaign.objects.all()

    def get_context_data(self, **kwargs):
        context = super(CampaignListView, self).get_context_data(**kwargs)
        qs = self.get_queryset()
        facet = self.kwargs['facet']
        context['facet'] = facet
        context['facet_label'] = FACET_LABELS.get(facet, 'Active')
        return context

class MergeView(FormView):
    template_name = "merge.html"
    work = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return render(request, "admins_only.html")
        else:
            return super(MergeView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MergeView, self).get_context_data(**kwargs)
        context['work'] = self.work
        return context

    def get_form_class(self):
        if self.request.method == 'POST' and 'confirm_merge_works' in self.request.POST:
            return WorkForm
        else:
            return OtherWorkForm

    def get_form_kwargs(self):
        self.work = safe_get_work(self.kwargs["work_id"])
        form_kwargs = {'work':self.work}
        if self.request.method == 'POST':
            form_kwargs.update({'data':self.request.POST})
        return form_kwargs

    def form_valid(self, form):
        other_work = form.cleaned_data['other_work']
        context = self.get_context_data()
        if 'confirm_merge_works' in self.request.POST:
            context['old_work_id'] = other_work.id
            self.work = merge_works(self.work, other_work, self.request.user)
            context['merge_complete'] = True
        else:
            context['form'] = WorkForm(initial={'other_work':other_work})
            context['other_work'] = other_work
        return render(self.request, self.template_name, context)

class GiftView(TemplateView):
    template_name = "gift.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        context['transfer_form'] = getTransferCreditForm(self.request.user.credit.available)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        transfer_form = getTransferCreditForm(self.request.user.credit.available, data=self.request.POST)
        if transfer_form.is_valid():
            if self.request.user.credit.transfer_to(transfer_form.cleaned_data['recipient'], transfer_form.cleaned_data['amount']):
                #successful transfer
                context['transfer_message'] = 'Your transfer has been successfully executed.'
                context['recipient'] = transfer_form.cleaned_data['recipient']
                context['transfer_amount'] = transfer_form.cleaned_data['amount']
                context['transfer_form'] = getTransferCreditForm(self.request.user.credit.available)
            else:
                #unsuccessful transfer
                context['transfer_message'] = 'Your transfer was not successful.'
                context['transfer_form'] = transfer_form
        else:
            #not valid
            context['transfer_form'] = transfer_form
        return self.render_to_response(context)

    def get_context_data(self, *args, **kwargs):
        context = {'user' : self.request.user}
        return context

class PledgeView(FormView):
    action = "pledge"
    template_name = "pledge.html"
    form_class = CampaignPledgeForm
    transaction = None
    campaign = None
    work = None
    premiums = None
    data = {}

    def get_preapproval_amount(self):
        preapproval_amount = self.request.GET.get('preapproval_amount', self.request.POST.get('preapproval_amount', None))
        if preapproval_amount:
            return preapproval_amount
        premium_id = self.request.GET.get('premium_id', self.request.POST.get('premium_id', None))
        if premium_id != None:
            try:
                preapproval_amount = D(models.Premium.objects.get(id=premium_id).amount)
            except:
                preapproval_amount = None
        if self.transaction:
            if preapproval_amount:
                preapproval_amount = preapproval_amount if preapproval_amount > self.transaction.amount else self.transaction.amount
            else:
                preapproval_amount = self.transaction.amount
        return preapproval_amount

    def get_form_kwargs(self):

        assert self.request.user.is_authenticated
        self.work = safe_get_work(self.kwargs["work_id"])

        # if there is no campaign or if campaign is not active, we should raise an error
        try:
            self.campaign = self.work.last_campaign()
             # TODO need to sort the premiums
            self.premiums = self.campaign.custom_premiums() | models.Premium.objects.filter(id=150)
            # Campaign must be ACTIVE
            assert self.campaign.status == 'ACTIVE'
        except Exception as e:
            # this used to raise an exception, but that seemed pointless. 
            # This now has the effect of preventing any pledges.
            return {}

        transactions = self.campaign.transactions().filter(
            user=self.request.user,
            status=TRANSACTION_STATUS_ACTIVE,
            type=PAYMENT_TYPE_AUTHORIZATION
        )
        premium_id = self.request.GET.get('premium_id', self.request.POST.get('premium_id', 150))
        if not transactions.exists():
            ack_name = self.request.user.profile.ack_name
            ack_dedication = ''
            anonymous = self.request.user.profile.anon_pref
        else:
            self.transaction = transactions[0]
            if premium_id == 150 and self.transaction.premium is not None:
                premium_id = self.transaction.premium.id
            if self.transaction.extra :
                ack_name = self.transaction.extra.get('ack_name', self.request.user.profile.ack_name)
                ack_dedication = self.transaction.extra.get('ack_dedication','')
            else:
                ack_name = self.request.user.profile.ack_name
                ack_dedication = ''
            anonymous = self.transaction.anonymous

        self.data = {'preapproval_amount':self.get_preapproval_amount(), 'premium_id':premium_id,
                    'ack_name':ack_name, 'ack_dedication':ack_dedication, 'anonymous':anonymous}
        if self.request.method  == 'POST':
            self.data.update(self.request.POST.dict())
            if not 'anonymous' in self.request.POST:
                del self.data['anonymous']
            if not 'ack_name' in self.request.POST:
                del self.data['ack_name']
            if not 'ack_dedication' in self.request.POST:
                del self.data['ack_dedication']
            return {'data':self.data}
        else:
            return {'initial':self.data}

    def get_context_data(self, **kwargs):
        """set up the pledge page"""

        context = super(PledgeView, self).get_context_data(**kwargs)

        context.update({
                'work':self.work,
                'campaign':self.campaign,
                'premiums':self.premiums,
                'premium_id':self.data.get('premium_id', None),
                'faqmenu': 'modify' if self.transaction else 'pledge',
                'transaction': self.transaction,
                'tid': self.transaction.id if self.transaction else None,
                'cover_width': cover_width(self.work)
           })

        return context

    def form_valid(self, form):
        # right now, if there is a non-zero pledge amount, go with that. 
        # otherwise, do the pre_approval
        donation = form.cleaned_data['donation']
        p = PaymentManager()
        if self.transaction:
            assert self.transaction.type == PAYMENT_TYPE_AUTHORIZATION and \
                    self.transaction.status == TRANSACTION_STATUS_ACTIVE

            if donation:
                # cancel transaction, then proceed to make a donation
                p.cancel_transaction(self.transaction)
            else:
                # modify the pledge...
                status,  url = p.modify_transaction(
                    self.transaction,
                    form.cleaned_data["preapproval_amount"],
                    paymentReason="Unglue.it %s for %s"% (self.action, self.campaign.name),
                    pledge_extra=form.trans_extra,
                )
                logger.info("status: {0}, url:{1}".format(status, url))

                if status and url is not None:
                    logger.info("PledgeView (Modify): " + url)
                    return HttpResponseRedirect(url)
                elif status and url is None:
                    return HttpResponseRedirect(
                        "{0}?tid={1}".format(reverse('pledge_modified'), self.transaction.id)
                    )
                else:
                    return HttpResponse("No modification made")

        t, url = p.process_transaction(
            'USD',
            form.amount(),
            host = PAYMENT_HOST_NONE,
            campaign=self.campaign,
            user=self.request.user,
            paymentReason=u"Unglue.it Pledge for {0}".format(self.campaign.name),
            pledge_extra=form.trans_extra,
            donation = donation
        )
        if url:
            logger.info("PledgeView url: " + url)
            return HttpResponseRedirect(url)
        else:
            logger.error("Attempt to produce transaction id {0} failed".format(t.id))
            return HttpResponse(
                "Our attempt to enable your transaction failed. We have logged this error."
            )

class PurchaseView(PledgeView):
    template_name = "purchase.html"
    form_class = CampaignPurchaseForm
    action = "purchase"
    offer_id = None

    def get_context_data(self, **kwargs):
        context = super(PledgeView, self).get_context_data(**kwargs)
        context.update({
                'work':self.work,
                'campaign':self.campaign,
                'faqmenu': 'purchase' ,
                'transaction': self.transaction,
                'tid': self.transaction.id if self.transaction else None,
                'cover_width': cover_width(self.work),
                'offer_id':self.offer_id,
                'user_license': self.work.get_user_license(self.request.user),
                'give': self.give
           })

        return context

    def get_form_kwargs(self):
        assert self.request.user.is_authenticated
        self.work = safe_get_work(self.kwargs["work_id"])

        # if there is no campaign or if campaign is not active, we should raise an error
        try:
            self.campaign = self.work.last_campaign()
            # Campaign must be ACTIVE
            assert self.campaign.status == 'ACTIVE'
        except Exception as e:
            # this used to raise an exception, but that seemed pointless. This now has the effect of preventing any pledges.
            return {}
        self.data = {
            'preapproval_amount':self.get_preapproval_amount(),
            'anonymous':self.request.user.profile.anon_pref,
            'offer_id': self.offer_id,
            }
        if self.request.method  == 'POST':
            data = self.request.POST.dict()
            data.update(self.data)
            self.data = data
            self.data['give'] = self.give
            if not 'anonymous' in self.request.POST:
                del self.data['anonymous']
            return {'data':self.data}
        else:
            return {'initial':self.data}

    def get_preapproval_amount(self):
        self.offer_id = self.request.GET.get('offer_id', self.request.POST.get('offer_id', None))
        self.give = self.offer_id.startswith('give') if self.offer_id else False
        if self.give:
            self.offer_id = self.offer_id[4:]
        if not self.offer_id and self.work.last_campaign() and self.work.last_campaign().individual_offer:
            self.offer_id = self.work.last_campaign().individual_offer.id
        preapproval_amount = None
        if self.offer_id != None:
            try:
                preapproval_amount = D(models.Offer.objects.get(id=self.offer_id).price)
            except:
                preapproval_amount = None
        return preapproval_amount

    def form_valid(self, form):
        p = PaymentManager()
        t, url = p.process_transaction('USD',  form.amount(),
                host = PAYMENT_HOST_NONE,
                campaign=self.campaign,
                user=self.request.user,
                paymentReason="Unglue.it Purchase for {0}".format(self.campaign.name),
                pledge_extra=form.trans_extra
                )
        if url:
            return HttpResponseRedirect(url)
        else:
            logger.error("Attempt to produce transaction id {0} failed".format(t.id))
            return HttpResponse("Our attempt to enable your transaction failed. We have logged this error.")

class NewDonationView(FormView):
    template_name = "fund_the_pledge.html"
    form_class = DonationForm
    def form_valid(self, form):
        p = PaymentManager()
        t, url = p.process_transaction('USD',  form.cleaned_data["amount"],
                                       user=self.request.user,
                                       paymentReason=form.cleaned_data.get("reason", ""),
                                      )
        if url:
            return HttpResponseRedirect(url)
        else:
            logger.error("Attempt to produce transaction id %s failed", t.id)
            return HttpResponse(
                "Our attempt to set up your donation failed.  We have logged this problem."
            )


class FundView(FormView):
    template_name = "fund_the_pledge.html"
    transaction = None
    action = None

    def get_form_class(self):
        if self.request.user.is_anonymous:
            return AnonCCForm
        elif self.request.user.profile.account:
            return AccountCCForm
        else:
            return CCForm

    def get_form_kwargs(self):
        kwargs = super(FundView, self).get_form_kwargs()
        if 'data' in kwargs:
            data = kwargs['data'].copy()
            kwargs['data'] = data
        else:
            data = {}
            kwargs['initial'] = data
        t_id=self.kwargs["t_id"]

        if self.transaction is None:
            try:
                self.transaction = get_object_or_404(Transaction, id=t_id)
            except ValueError:
                raise Http404


        if not self.transaction.campaign:
            self.action = 'donation'
        elif self.transaction.campaign.type == REWARDS:
            self.action = 'donation' if self.transaction.donation else 'pledge'
        elif self.transaction.campaign.type == THANKS:
            self.action = 'contribution'
        else:
            self.action = 'purchase'


        data.update(
            {'preapproval_amount':self.transaction.needed_amount,
                'username':self.request.user.username if self.request.user.is_authenticated else None,
                'work_id':self.transaction.campaign.work_id if self.transaction.campaign else None,
                'title':self.transaction.campaign.work.title if self.transaction.campaign else COMPANY_TITLE}
            )
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(FundView, self).get_context_data(**kwargs)
        context['modified'] = self.transaction.status == TRANSACTION_STATUS_MODIFIED
        context['preapproval_amount'] = self.transaction.max_amount
        context['needed'] = self.transaction.needed_amount
        context['transaction'] = self.transaction
        context['STRIPE_PK'] = stripelib.STRIPE_PK
        context['action'] = self.action
        return context

    def form_valid(self, form):
        p = PaymentManager()
        stripe_token = form.cleaned_data.get("stripe_token", None)
        self.transaction.host = settings.PAYMENT_PROCESSOR
        return_url = "%s?tid=%s" % (reverse('pledge_complete'), self.transaction.id)

        if not self.transaction.campaign:
            if self.request.user.is_authenticated:
                self.transaction.user = self.request.user
            # if there's an email address, put it in the receipt column, so far unused.
            self.transaction.receipt = form.cleaned_data.get("email", None)
            t, url = p.charge(self.transaction, return_url = return_url, token=stripe_token)

        elif self.transaction.campaign.type == THANKS and self.transaction.user == None:
            #anonymous user, just charge the card!
            if self.request.user.is_authenticated:
                self.transaction.user = self.request.user
            # if there's an email address, put it in the receipt column, so far unused.
            self.transaction.receipt = form.cleaned_data.get("email", None)
            t, url = p.charge(self.transaction, return_url = return_url, token=stripe_token)
        elif self.request.user.is_anonymous:
            #somehow the user lost their login
            return HttpResponseRedirect(reverse('superlogin'))
        elif self.transaction.user.id != self.request.user.id:
            # other sort of strange trouble!
            return render(self.request, "pledge_user_error.html", {'transaction': self.transaction, 'action': self.action })
        else:
            # if the user has  active account, use it. Otherwise...
            if not self.request.user.profile.account:

                # if we get a stripe_token, create a new stripe account for the user
                if stripe_token:
                    try:
                        p.make_account(user=self.request.user, host=settings.PAYMENT_PROCESSOR, token=stripe_token)
                    except baseprocessor.ProcessorError as e:
                        return render(self.request, "pledge_card_error.html", {'transaction': self.transaction, 'exception':e })
                else: # empty token
                    e = baseprocessor.ProcessorError("Empty token")
                    return render(self.request, "pledge_card_error.html", {'transaction': self.transaction, 'exception':e })
            # with the Account in hand, now do the transaction
            if self.action == 'pledge':
                t, url = p.authorize(self.transaction, return_url =  return_url)
            else:
                t, url = p.charge(self.transaction, return_url = return_url)

        # redirecting user to pledge_complete/payment_complete on successful preapproval (in the case of stripe)
        if url is not None:
            return HttpResponseRedirect(url)
        else:
            return render(self.request, "pledge_card_error.html", {'transaction': self.transaction })

class GiftCredit(TemplateView):
    template_name = "gift_credit.html"

    def get_context_data(self, **kwargs):
        context = super(GiftCredit, self).get_context_data(**kwargs)
        context['faqmenu'] = "gift"
        try:
            envelope = signing.loads(kwargs['token'])
            context['envelope'] = envelope
        except signing.BadSignature:
            self.template_name = "gift_error.html"
            return context
        try:
            work = models.Work.objects.get(id=envelope['work_id'])
            campaign = work.last_campaign()
        except models.Work.DoesNotExist:
            campaign = None
        context['work'] = work
        try:
            user = User.objects.get(username=envelope['username'])
        except User.DoesNotExist:
            self.template_name = "gift_user_error.html"
            context['error'] = 'user does not exist'
            return context
        if user != self.request.user:
            self.template_name = "gift_user_error.html"
            context['error'] = 'wrong user logged in'
            return context
        try:
            # check token not used
            CreditLog.objects.get(sent=envelope['sent'])
            context['error'] = 'credit already registered'
            return context
        except CreditLog.DoesNotExist:
            #not used yet!
            amount = envelope['amount'] + envelope['cents'] // D(100)
            CreditLog.objects.create(user=user, amount=amount, action='deposit', sent=envelope['sent'])
            ts = Transaction.objects.filter(user=user, campaign=campaign, status=TRANSACTION_STATUS_NONE).order_by('-pk')
            if not ts.exists():
                ts = Transaction.objects.filter(user=user, campaign=campaign, status=TRANSACTION_STATUS_MODIFIED).order_by('-pk')
            if ts.exists():
                t = ts[0]
                credit_transaction(t, user, amount)
                for t in ts[1:]:
                    t.status = TRANSACTION_STATUS_CANCELED
                    t.save()
                context['transaction'] = t
                return context
            else:
                user.credit.add_to_balance(amount)
                return context


class PledgeRechargeView(TemplateView):
    """
    a view to allow for recharge of a transaction for failed transactions or ones with errors
    """
    template_name = "pledge_recharge.html"

    def get_context_data(self, **kwargs):

        context = super(PledgeRechargeView, self).get_context_data(**kwargs)

        # the following should be true since PledgeView.as_view is wrapped in login_required
        assert self.request.user.is_authenticated
        user = self.request.user

        work = safe_get_work(self.kwargs["work_id"])
        campaign = work.last_campaign()

        if campaign is None:
            raise Http404

        transaction = campaign.transaction_to_recharge(user)

        # calculate a URL to do a preapproval -- in the future, we may want to do a straight up payment

        return_url = None
        nevermind_url = None

        if transaction is not None:
            # the recipients of this authorization is not specified here but rather by the PaymentManager.
            paymentReason = "Unglue.it Recharge for {0}".format(campaign.name)

            p = PaymentManager()
            t, url = p.authorize(transaction, return_url=return_url, paymentReason=paymentReason)
            logger.info("Recharge url: {0}".format(url))
        else:
            url = None

        context.update({
                'work':work,
                'transaction':transaction,
                'payment_processor':transaction.host if transaction is not None else None,
                'recharge_url': url
                })
        return context


class FundCompleteView(TemplateView):
    """A callback for Payment to tell unglue.it that a payment transaction has completed successfully.

    Possible things to implement:

        after pledging, supporter receives email including thanks, work pledged, amount, expiry date, any next steps they should expect; others?
    study other confirmation emails for their contents
    should note that a confirmation email has been sent to $email from $sender
    should briefly note next steps (e.g. if this campaign succeeds you will be emailed on date X)

    """

    template_name = "pledge_complete.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if self.transaction:
            if not self.transaction.campaign:
                return self.render_to_response(context)
            if self.transaction.campaign.type == THANKS:
                return DownloadView.as_view()(request, work=self.transaction.campaign.work)

            else:
                if request.user.is_authenticated:
                    if self.user_is_ok():
                        return self.render_to_response(context)
                    else:
                        return HttpResponseRedirect(reverse('work', kwargs={'work_id': self.transaction.campaign.work_id}))
                else:
                    return redirect_to_login(request.get_full_path())
        else:
            return HttpResponseRedirect(reverse('home'))

    def user_is_ok(self):
        if not self.transaction:
            return False
        if (not self.transaction.campaign or self.transaction.campaign.type == THANKS) and self.transaction.user == None:
            # to handle anonymous donors- leakage not an issue
            return True
        else:
            return self.request.user.id == self.transaction.user_id



    def get_context_data(self):
        # pick up all get and post parameters and display
        context = super(FundCompleteView, self).get_context_data()
        self.transaction = None

        # pull out the transaction id and try to get the corresponding Transaction
        transaction_id = self.request.POST.get("tid", self.request.GET.get("tid", None))

        if not transaction_id:
            return context
        try:
            self.transaction = Transaction.objects.get(id=transaction_id)
        except (ValueError, Transaction.DoesNotExist):
            self.transaction = None

        if not self.transaction:
            return context

        # work and campaign in question
        try:
            campaign = self.transaction.campaign
            work = campaign.work
        except Exception as e:
            campaign = None
            work = None

        # # we need to check whether the user tied to the transaction is indeed the authenticated user.

        if not self.user_is_ok():
            return context

        gift = 'give_to' in self.transaction.extra
        if not gift:
            # add the work corresponding to the Transaction on the user's wishlist if it's not already on the wishlist
            if self.transaction.user is not None and (campaign is not None) and (work is not None):
                self.transaction.user.wishlist.add_work(work, 'pledging', notify=True)

        #put info into session for download page to pick up.
            self.request.session['amount'] = int(self.transaction.amount * 100)
            if self.transaction.receipt:
                self.request.session['receipt'] = self.transaction.receipt

        context["transaction"] = self.transaction
        context["work"] = work
        context["campaign"] = campaign
        context["faqmenu"] = "complete"
        context["site"] = Site.objects.get_current()

        return context

class PledgeModifiedView(FundCompleteView):
    def get_context_data(self):
        context = super(PledgeModifiedView, self).get_context_data()
        context['modified'] = True
        return context

class PledgeCancelView(FormView):
    """A view for allowing a user to cancel the active transaction for specified campaign"""
    template_name = "pledge_cancel.html"
    form_class = PledgeCancelForm

    def get_context_data(self, **kwargs):
        context = super(PledgeCancelView, self).get_context_data(**kwargs)

        # initialize error to be None
        context["error"] = None

        # the following should be true since PledgeCancelView.as_view is wrapped in login_required

        if self.request.user.is_authenticated:
            user = self.request.user
        else:
            context["error"] = "You are not logged in."
            return context
        
        try:
            campaign = get_object_or_404(models.Campaign, id=self.kwargs["campaign_id"])
        except ValueError:
            raise Http404

        if campaign.status != 'ACTIVE':
            context["error"] = "{0} is not an active campaign".format(campaign)
            return context

        work = campaign.work
        transactions = campaign.transactions().filter(user=user, status=TRANSACTION_STATUS_ACTIVE)

        if not transactions.exists():
            context["error"] = "You don't have an active transaction for this campaign."
            return context
        elif transactions.count() > 1:
            logger.error("User {0} has {1} active transactions for campaign id {2}".format(user, transactions.count(), campaign.id))
            context["error"] = "You have {0} active transactions for this campaign".format(transactions.count())
            return context

        transaction = transactions[0]
        if transaction.type != PAYMENT_TYPE_AUTHORIZATION:
            logger.error("Transaction id {0} transaction type, which should be {1}, is actually {2}".format(transaction.id, PAYMENT_TYPE_AUTHORIZATION, transaction.type))
            context["error"] = "Your transaction type, which should be {0}, is actually {1}".format(PAYMENT_TYPE_AUTHORIZATION, transaction.type)
            return context

        # we've located the transaction, work, and campaign referenced in the view

        context["transaction"] = transaction
        context["work"] = work
        context["campaign"] = campaign
        context["faqmenu"] = "cancel"

        return context

    def form_valid(self, form):
        # check that user does, in fact, have an active transaction for specified campaign

        logger.info("arrived at pledge_cancel form_valid")
        # pull campaign_id from form, not from URI as we do from GET
        campaign_id = self.request.POST.get('campaign_id', self.request.GET.get('campaign_id'))

        # this following logic should be extraneous.
        if self.request.user.is_authenticated:
            user = self.request.user
        else:
            return HttpResponse("You need to be logged in.")

        try:
            # look up the specified campaign and attempt to pull up the appropriate transaction
            # i.e., the transaction actually belongs to user, that the transaction is active
            try:
                campaign = get_object_or_404(models.Campaign, id=self.kwargs["campaign_id"], status='ACTIVE')
            except ValueError:
                raise Http404

            transaction = campaign.transaction_set.get(user=user, status=TRANSACTION_STATUS_ACTIVE,
                                                          type=PAYMENT_TYPE_AUTHORIZATION)
            # attempt to cancel the transaction and redirect to the Work page if cancel is successful
            # here's a place that would be nice to use https://docs.djangoproject.com/en/dev/ref/contrib/messages/
            # to display the success or failure of the cancel operation as a popup in the context of the work page
            p = PaymentManager()
            result = p.cancel_transaction(transaction)
            # put a notification here for pledge cancellation?
            if result:
                # Now if we redirect the user to the Work page and the IPN hasn't arrived, the status of the
                # transaction might be out of date.  Let's try an explicit polling of the transaction result before redirecting
                # We might want to remove this in a production system
                if settings.DEBUG:
                    update_status = p.update_preapproval(transaction)
                # send a notice out that the transaction has been canceled -- leverage the pledge_modify notice for now
                # BUGBUG:  should have a pledge cancel notice actually since I think it's different
                from regluit.payment.signals import pledge_modified
                pledge_modified.send(sender=self, transaction=transaction, up_or_down="canceled")
                logger.info("pledge_modified notice for cancellation: sender {0}, transaction {1}".format(self, transaction))
                return HttpResponseRedirect(reverse('work', kwargs={'work_id': campaign.work_id}))
            else:
                logger.error("Attempt to cancel transaction id {0} failed".format(transaction.id))
                return HttpResponse("Our attempt to cancel your transaction failed. We have logged this error.")
        except Exception as e:
            logger.error("Exception from attempt to cancel pledge for campaign id {0} for username {1}: {2}".format(campaign_id, user.username, e))
            return HttpResponse("Sorry, something went wrong in canceling your campaign pledge. We have logged this error.")

def works_user_can_admin(user):
    return models.Work.objects.filter(
        Q(claim__user = user) | Q(claim__rights_holder__owner = user)
        )


def campaign_admin(request):
    if not request.user.is_authenticated:
        return render(request, "admins_only.html")
    if not request.user.is_staff :
        return render(request, "admins_only.html")

    context = {}

    def campaigns_types():
        # pull out Campaigns with Transactions that are ACTIVE -- and hence can be executed
        # Campaign.objects.filter(transaction__status='ACTIVE')

        campaigns_with_active_transactions = models.Campaign.objects.filter(transaction__status=TRANSACTION_STATUS_ACTIVE)

        # pull out Campaigns with Transactions that are INCOMPLETE

        campaigns_with_incomplete_transactions = models.Campaign.objects.filter(transaction__status=TRANSACTION_STATUS_INCOMPLETE)

        # show all Campaigns with Transactions that are COMPLETED

        campaigns_with_completed_transactions = models.Campaign.objects.filter(transaction__status=TRANSACTION_STATUS_COMPLETE)

        # show Campaigns with Transactions that are CANCELED

        campaigns_with_canceled_transactions = models.Campaign.objects.filter(transaction__status=TRANSACTION_STATUS_CANCELED)

        return (campaigns_with_active_transactions, campaigns_with_incomplete_transactions, campaigns_with_completed_transactions, campaigns_with_canceled_transactions)

    form = CampaignAdminForm()
    pm = PaymentManager()
    check_status_results = None
    command_status = None

    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        if 'campaign_checkstatus' in request.POST.keys():
            # campaign_checkstatus
            try:
                status = pm.checkStatus()
                check_status_results = ""
                # parse the output to display chat transaction statuses have been updated
                if len(status["preapprovals"]):
                    for t in status["preapprovals"]:
                        check_status_results += "<p>Preapproval key: %s updated</p>" % (t["key"])
                else:
                    check_status_results += "<p>No preapprovals needed updating</p>"
                if len(status["payments"]):
                    for t in status["payments"]:
                        info = ", ".join(["%s:%s" % (k, v) for (k, v) in t.items()])
                        check_status_results += "<p>Payment updated: %s </p>" % (info)

                else:
                    check_status_results += "<p>No payments needed updating</p>"
                command_status = _("Transactions updated based on PaymentDetails and PreapprovalDetails")
            except Exception as e:
                check_status_results = e
        elif 'execute_campaigns' in request.POST.keys():
            c_id = request.POST.get('active_campaign', None)
            if c_id is not None:
                try:
                    campaign = models.Campaign.objects.get(id=c_id)
                    results = pm.execute_campaign(campaign)
                    command_status = str(results)
                except Exception as e:
                    command_status = "Error in executing transactions for campaign %s " % (str(e))
        elif 'finish_campaigns' in request.POST.keys():
            c_id = request.POST.get('incomplete_campaign', None)
            if c_id is not None:
                try:
                    campaign = models.Campaign.objects.get(id=c_id)
                    results = pm.finish_campaign(campaign)
                    command_status = str(results)
                except Exception as e:
                    command_status = "Error in finishing transactions for campaign %s " % (str(e))

        elif 'cancel_campaigns' in request.POST.keys():
            c_id = request.POST.get('active_campaign', None)
            if c_id is not None:
                try:
                    campaign = models.Campaign.objects.get(id=c_id)
                    results = pm.cancel_campaign(campaign)
                    command_status = str(results)
                except Exception as e:
                    command_status = "Error in canceling transactions for campaign %s " % (str(e))

    (campaigns_with_active_transactions, campaigns_with_incomplete_transactions, campaigns_with_completed_transactions,
                campaigns_with_canceled_transactions) = campaigns_types()

    context.update({
        'form': form,
        'check_status_results':check_status_results,
        'campaigns_with_active_transactions': campaigns_with_active_transactions,
        'campaigns_with_incomplete_transactions': campaigns_with_incomplete_transactions,
        'campaigns_with_completed_transactions': campaigns_with_completed_transactions,
        'campaigns_with_canceled_transactions': campaigns_with_canceled_transactions,
        'command_status': command_status
    })

    return render(request, "campaign_admin.html", context)

def supporter(request, supporter_username, template_name, extra_context={}):
    supporter = get_object_or_404(User, username=supporter_username)
    wishlist = supporter.wishlist
    works_unglued = []
    works_active = []
    works_wished = []
    works_on_wishlist = wishlist.works.all()

    if (works_on_wishlist):
        # querysets for tabs
        # unglued tab is anything with an existing ebook or successful campaign
        ## .order_by() may clash with .distinct() and this should be fixed
        unglueit_works = works_on_wishlist.filter(campaigns__status="SUCCESSFUL").distinct()
        works_otherwise_available = works_on_wishlist.filter(is_free = True).distinct()
        works_unglued = unglueit_works | works_otherwise_available
        works_unglued = works_unglued.order_by('-campaigns__status', 'campaigns__deadline', '-num_wishes')

        works_active = works_on_wishlist.filter(campaigns__status='ACTIVE').order_by('campaigns__deadline').distinct()

        # everything else goes in tab 3
        works_wished = works_on_wishlist.exclude(pk__in=works_active.values_list('pk', flat=True)).exclude(pk__in=works_unglued.values_list('pk', flat=True)).order_by('-num_wishes')

        slidelist = []
        # badge counts
        backed = works_unglued.count()
        backing = works_active.count()
        wished = works_wished.count()

    else:
        backed = 0
        backing = 0
        wished = 0
        slidelist = slideshow()
    # default to showing the Active tab if there are active campaigns, else show Wishlist
    if backing > 0:
        activetab = "#2"
    elif wished == 0:
        activetab = "#1"
    else:
        activetab = "#3"

    # following block to support profile admin form in supporter page
    if request.user.is_authenticated and request.user.username == supporter_username:

        profile_obj = request.user.profile

        if  request.method == 'POST':
            profile_form = ProfileForm(data=request.POST, instance=profile_obj)
            if profile_form.is_valid():
                profile_form.save()

        else:
            profile_form = ProfileForm(instance=profile_obj)

    else:
        profile_form = ''

    process_kindle_email(request)
    context = {
            "supporter": supporter,
            "wishlist": wishlist,
            "works_unglued": works_unglued,
            "works_active": works_active,
            "works_wished": works_wished,
            "slidelist": slidelist,
            "backed": backed,
            "backing": backing,
            "wished": wished,
            "profile_form": profile_form,
            "activetab": activetab,
    }
    context.update(extra_context)
    return render(request, template_name, context)

def library(request, library_name):
    context = {}
    try:
        # determine if the supporter is a library
        authenticator = Authenticator(request, library_name)
        context['authenticator'] = authenticator
        context['library'] = library = authenticator.library
    except Library.DoesNotExist:
        raise Http404
    works_active = models.Work.objects.filter(acqs__user=library.user, acqs__license=LIBRARY).distinct()
    if works_active.exists():
        context['works_active'] = works_active
        context['activetab'] = "#2"
    context['ungluers'] = userlists.library_users(library, 5)
    return supporter(request, library_name, template_name='libraryauth/library.html', extra_context=context)



class ManageAccount(FormView):
    template_name = "manage_account.html"
    form_class = PlainCCForm

    def get_context_data(self, **kwargs):
        context = super(ManageAccount, self).get_context_data(**kwargs)
        context['STRIPE_PK'] = stripelib.STRIPE_PK
        return context

    def form_valid(self, form):
        """ save the token, make an account"""

        p = PaymentManager()
        stripe_token = form.cleaned_data["stripe_token"]
        # if we get a stripe_token, create a new stripe account for the user
        if stripe_token:
            try:
                p.make_account(user=self.request.user, host=settings.PAYMENT_PROCESSOR, token=stripe_token)
            except baseprocessor.ProcessorError as e:
                return render(self.request, "pledge_card_error.html", {'exception':e})
        next = self.request.GET.get('next', self.request.POST.get('next', None))
        if next :
            return HttpResponseRedirect(next)
        else:
            return render(self.request, self.template_name, self.get_context_data())

def search(request):
    """
    request params 
    q the query
    ty type  - au is author, g or anything else is general
    gbo  >0 = start in google books 0 = start in unglue.it
    page = page number for unglue.it results
    gbpage = page number for google results
    
    max 10 items per page from either unglue.it or gb
    possible results - 1 page of unglue.it results
                     - an additional page of unglue.it
                     - the last page of ungluit
                     - beginning of gb, 
                     - more from gb.
                     
    
    """
    q = request.GET.get('q', '').strip()
    ty = request.GET.get('ty', 'g')  # ge= 'general, au= 'author'
    if not cf.validate(request):
        context = {
            "q": q,
            "ty": ty,
            "results": [],
            "ug_works": [],
            "ug_more": 'no',
        }
        return render(request, 'search.html', context)

    request.session['q'] = q
    gbo = request.GET.get('gbo', '0') # gbo says where to start
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        # garbage in page
        page = 1
    try:
        gbpage = int(request.GET.get('gbpage', 1))
    except ValueError:
        # garbage in page
        gbpage = 1
   
    start = (page - 1) * 10
    end = page * 10 

    our_stuff =  Q(is_free=True)
    out = []
    if len(q) > 1 and gbo == '0':
        isbnq = ISBN(q)
        if isbnq.valid:
            work_query = Q(identifiers__value=str(isbnq), identifiers__type="isbn")
        elif ty == 'au':
            work_query =  Q(editions__authors__name=q)
        else:
            work_query = Q(title__istartswith=q)
        ug_works = models.Work.objects.filter(our_stuff).filter(work_query).distinct()
        out = ug_works[start:end]

    if len(out) < 10:
        ug_more = 'no'
        page = 1

        if is_bad_robot(request):
            results = models.Work.objects.none()
        else:
            results = gluejar_search(q, user_ip=request.META['REMOTE_ADDR'], page=gbpage)

    elif not ug_works[10:11]:
        ug_more = 'no'
        results = gluejar_search(q, user_ip=request.META['REMOTE_ADDR'], page=1)

    else:
        ug_more = 'yes'
        results = models.Work.objects.none()

    # flag search result as on wishlist as appropriate
    works = []
    for result in results:
        try:
            work = models.Identifier.objects.get(type='goog', value=result['googlebooks_id']).work
            works.append(work)
        except models.Identifier.DoesNotExist:
            works.append(result)
    context = {
        "q": q,
        "ty": ty,
        "results": works,
        "ug_works": out,
        "ug_more": ug_more
    }
    return render(request, 'search.html', context)

# TODO: perhaps this functionality belongs in the API?
@require_POST
@login_required
@csrf_exempt
def wishlist(request):
    googlebooks_id = request.POST.get('googlebooks_id', None)
    remove_work_id = request.POST.get('remove_work_id', None)
    add_work_id = request.POST.get('add_work_id', None)
    setkw = request.POST.get('setkw', None)
    if setkw and request.user.is_staff:
        try:
            subject = models.Subject.objects.get(name=setkw)
        except models.Subject.DoesNotExist:
            return HttpResponse('invalid subject')
        if remove_work_id:
            work = safe_get_work(int(remove_work_id))
            work.subjects.remove(subject)
            return HttpResponse('removed work from '+setkw)
        elif add_work_id:
            work = safe_get_work(add_work_id)
            work.subjects.add(subject)
            return HttpResponse('added work to '+setkw)

    if googlebooks_id:
        try:
            edition = bookloader.add_by_googlebooks_id(googlebooks_id)
            if edition.new:
                # add related editions asynchronously
                tasks.populate_edition.delay(edition.isbn_13)
            request.user.wishlist.add_work(edition.work, 'user', notify=True)
            return HttpResponse('added googlebooks id')
        except bookloader.LookupFailure:
            logger.warning("failed to load googlebooks_id %s" % googlebooks_id)
            return HttpResponse('error adding googlebooks id')
        except Exception as e:
            logger.warning("Error in wishlist adding %s" % (e))
            return HttpResponse('error adding googlebooks id')
        # TODO: redirect to work page, when it exists
    elif remove_work_id:
        work = safe_get_work(int(remove_work_id))
        request.user.wishlist.remove_work(work)
        return HttpResponse('removed work from wishlist')
    elif add_work_id:
        # if adding from work page, we have may work.id, not googlebooks_id
        work = safe_get_work(add_work_id)
        request.user.wishlist.add_work(work, 'user', notify=True)
        return HttpResponse('added work to wishlist')

@require_POST
@login_required
def kw_edit(request, work_id):
    work = safe_get_work(work_id)
    remove_kw = request.POST.get('remove_kw', None)
    add_form = request.POST.get('kw_add', False) # signal to process form
    if user_can_edit_work(request.user, work):
        if remove_kw:
            try:
                subject = models.Subject.objects.get(name=remove_kw)
            except models.Subject.DoesNotExist:
                return HttpResponse('invalid subject')
            work.subjects.remove(subject)
            return HttpResponse('removed ' + remove_kw)
        elif add_form:
            form = SubjectSelectForm(data=request.POST)
            if form.is_valid():
                add_kw = form.cleaned_data['add_kw']
                try:
                    subject = models.Subject.objects.get(name=add_kw)
                except models.Subject.DoesNotExist:
                    return HttpResponse('invalid subject')
                work.subjects.add(subject)
                return HttpResponse(add_kw.name)
            else:
                return HttpResponse('xxbadform')
        else:
            return HttpResponse(str(add_form))
    return HttpResponse(str(add_form))


class InfoPageView(TemplateView):

    template_name = 'metrics.html'

    def get_template_names(self, **kwargs):
        if self.kwargs['template_name']:
            return [self.kwargs['template_name'], self.template_name]
        else:
            return [self.template_name]

    def get_context_data(self, **kwargs):
        users = User.objects
        users.today = users.filter(date_joined__range = (date_today(), now()))
        users.days7 = users.filter(date_joined__range = (date_today()-timedelta(days=7), now()))
        users.year = users.filter(date_joined__year = date_today().year)
        users.month = users.year.filter(date_joined__month = date_today().month)
        users.yesterday = users.filter(date_joined__range = (date_today()-timedelta(days=1), date_today()))
        users.lt = users.exclude(profile__librarything_id = '')
        users.libtools = users.filter(libpref__isnull = False)
        works = models.Work.objects
        works.today = works.filter(created__range = (date_today(), now()))
        works.days7 = works.filter(created__range = (date_today()-timedelta(days=7), now()))
        works.year = works.filter(created__year = date_today().year)
        works.month = works.year.filter(created__month = date_today().month)
        works.yesterday = works.filter(created__range = (date_today()-timedelta(days=1), date_today()))
        works.wishedby2 = works.filter(num_wishes__gte = 2)
        works.wishedby20 = works.filter(num_wishes__gte = 20)
        works.wishedby5 = works.filter(num_wishes__gte = 5)
        works.wishedby50 = works.filter(num_wishes__gte = 50)
        works.wishedby10 = works.filter(num_wishes__gte = 10)
        works.wishedby100 = works.filter(num_wishes__gte = 100)
        works.free = works.filter(is_free = True)
        ebooks = models.Ebook.objects
        ebooks.today = ebooks.filter(created__range = (date_today(), now()))
        ebooks.days7 = ebooks.filter(created__range = (date_today()-timedelta(days=7), now()))
        ebooks.year = ebooks.filter(created__year = date_today().year)
        ebooks.month = ebooks.year.filter(created__month = date_today().month)
        ebooks.yesterday = ebooks.filter(created__range = (date_today()-timedelta(days=1), date_today()))
        ebooks.downloads = ebooks.aggregate(total=Sum('download_count'))['total']
        ebooks.pdfdownloads = ebooks.filter(format='pdf').aggregate(total=Sum('download_count'))['total']
        ebooks.epubdownloads = ebooks.filter(format='epub').aggregate(total=Sum('download_count'))['total']
        ebooks.mobidownloads = ebooks.filter(format='mobi').aggregate(total=Sum('download_count'))['total']
        ebookfiles = models.EbookFile.objects
        ebookfiles.today = ebookfiles.filter(created__range = (date_today(), now()))
        ebookfiles.days7 = ebookfiles.filter(created__range = (date_today()-timedelta(days=7), now()))
        ebookfiles.year = ebookfiles.filter(created__year = date_today().year)
        ebookfiles.month = ebookfiles.year.filter(created__month = date_today().month)
        ebookfiles.yesterday = ebookfiles.filter(created__range = (date_today()-timedelta(days=1), date_today()))
        wishlists = models.Wishlist.objects.exclude(wishes__isnull=True)
        wishlists.today = wishlists.filter(created__range = (date_today(), now()))
        wishlists.days7 = wishlists.filter(created__range = (date_today()-timedelta(days=7), now()))
        wishlists.year = wishlists.filter(created__year = date_today().year)
        wishlists.month = wishlists.year.filter(created__month = date_today().month)
        if date_today().day==1:
            wishlists.yesterday = wishlists.filter(created__range = (date_today()-timedelta(days=1), date_today()))
        else:
            wishlists.yesterday = wishlists.month.filter(created__day = date_today().day-1)

        transactions = Transaction.objects.filter(status__in = [TRANSACTION_STATUS_ACTIVE, TRANSACTION_STATUS_COMPLETE])
        transactions.sum = transactions.aggregate(Sum('amount'))['amount__sum']
        transactions.today = transactions.filter(date_created__range = (date_today(), now()))
        transactions.today.sum = transactions.today.aggregate(Sum('amount'))['amount__sum']
        transactions.days7 = transactions.filter(date_created__range = (date_today()-timedelta(days=7), now()))
        transactions.days7.sum = transactions.days7.aggregate(Sum('amount'))['amount__sum']
        transactions.year = transactions.filter(date_created__year = date_today().year)
        transactions.year.sum = transactions.year.aggregate(Sum('amount'))['amount__sum']
        transactions.month = transactions.year.filter(date_created__month = date_today().month)
        transactions.month.sum = transactions.month.aggregate(Sum('amount'))['amount__sum']
        transactions.yesterday = transactions.filter(date_created__range = (date_today()-timedelta(days=1), date_today()))
        transactions.yesterday.sum = transactions.yesterday.aggregate(Sum('amount'))['amount__sum']
        marc = apps.get_model('marc','MARCRecord').objects
        marc.today = marc.filter(created__range = (date_today(), now()))
        marc.days7 = marc.filter(created__range = (date_today()-timedelta(days=7), now()))
        marc.year = marc.filter(created__year = date_today().year)
        marc.month = marc.year.filter(created__month = date_today().month)
        marc.yesterday = marc.filter(created__range = (date_today()-timedelta(days=1), date_today()))
        return {
            'users': users,
            'works': works,
            'ebooks': ebooks,
            'ebookfiles': ebookfiles,
            'wishlists': wishlists,
            'transactions': transactions,
            'marc': marc,
        }

class InfoLangView(InfoPageView):

    template_name = 'languages.html'

    def get_context_data(self, **kwargs):
        languages = models.Work.objects.filter(num_wishes__gte = 1).values('language').annotate(lang_count=Count('language')).order_by('-lang_count')
        return {
            'wished_languages': languages,
        }

class FAQView(FormView):
    template_name = "faq.html"
    form_class = DateCalculatorForm

    def form_valid(self, form):
        form.instance.status = 'DEMO'
        form.instance.type = BUY2UNGLUE
        form.instance.set_dollar_per_day()
        form.instance.update_left()
        form.instance._current_total = form.cleaned_data['revenue']
        return self.render_to_response(self.get_context_data(form=form))

    def get_initial(self):
        return {'target':10000, 'cc_date_initial': date_today()+timedelta(days=1461), 'revenue':0, 'type':BUY2UNGLUE, 'status':'DEMO'}

    def get_context_data(self, **kwargs):
        cd = super(FAQView, self).get_context_data(**kwargs)
        cd.update({
                'location': self.kwargs["location"],
                'sublocation': self.kwargs["sublocation"],
                })
        return cd





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
        logger.info('Adding task to load librarything %s to user %s', lt_username, user)
        load_task_name = "load_librarything_into_wishlist"
        load_task = getattr(tasks, load_task_name)
        task_id = load_task.delay(user.id, lt_username, None)

        ct = models.CeleryTask()
        ct.task_id = task_id
        ct.function_name = load_task_name
        ct.user = user
        ct.description = "Loading LibraryThing collection of %s to user %s." % (lt_username, user)
        ct.save()

        return HttpResponse("<span style='margin: auto 10px auto 36px;vertical-align: middle;display: inline-block;'>We're on it! <a href='JavaScript:window.location.reload()'>Reload the page</a> to see the books we've snagged so far.</span>")
    except Exception as e:
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
    except Exception as e:
        logger.info("Error in clearing wishlist for user %s: %s ", request.user, e)
        return HttpResponse("Error in clearing wishlist: %s " % (e))

@require_POST
@login_required
def msg(request):
    form = MsgForm(data=request.POST)
    if form.is_valid():
        if not request.user.is_staff and request.user not in form.cleaned_data['work'].last_campaign().managers.all():
            logger.warning("unauthorized attempt to send message by %s for %s"% (request.user, form.cleaned_data['work']))
            raise Http404
        supporter_message.send(sender=request.user, msg=form.cleaned_data["msg"], work=form.cleaned_data["work"], supporter=form.cleaned_data["supporter"])
        return HttpResponse("message sent")
    else:
        logger.info("Invalid form for user %s", request.user)
        raise Http404


class LibraryThingView(FormView):
    template_name = "librarything.html"
    form_class = LibraryThingForm

    def get_context_data(self, **kwargs):
        context = super(LibraryThingView, self).get_context_data(**kwargs)
        form = kwargs['form']
        # get the books for the lt_username in the form
        lt_username = self.request.GET.get("lt_username", None)
        if lt_username is not None:
            lt = librarything.LibraryThing(username=lt_username)
            context.update({'books':list(lt.parse_user_catalog(view_style=5))})
        else:
            context.update({'books':None})


        return context

    def form_valid(self, form):
        return super(LibraryThingView, self).form_valid(form)

@require_POST
@login_required
@csrf_exempt
def clear_celery_tasks(request):
    try:
        request.user.tasks.clear()
        logger.info("Celery tasks for user %s cleared", request.user)
        return HttpResponse('Celery Tasks List cleared')
    except Exception as e:
        logger.info("Error in clearing Celery Tasks for user %s: %s ", request.user, e)
        return HttpResponse("Error in clearing Celery Tasks: %s " % (e))

def celery_test(request):
    return HttpResponse("celery_test")

# routing views that try to redirect to the works page on a 3rd party site
#
# TODO: need to queue up a task to look up IDs if we have to fallback to
# routing based on ISBN or search

def work_librarything(request, work_id):
    work = safe_get_work(work_id)
    isbn = work.first_isbn_13()
    if work.librarything_id:
        url = work.librarything_url
    elif isbn:
        # TODO: do the redirect here and capture the work id?
        url = "https://www.librarything.com/isbn/%s" % isbn
    else:
        term = work.title + " " + work.author()
        q = urlencode({'searchtpe': 'work', 'term': term})
        url = "https://www.librarything.com/search.php?" + q
    return HttpResponseRedirect(url)

def work_openlibrary(request, work_id):
    work = safe_get_work(work_id)
    url = None

    if work.openlibrary_id:
        url = work.openlibrary_url
    # fall back to doing a search on openlibrary
    if not url:
        q = urlencode({'q': work.title + " " + work.author()})
        url = "https://openlibrary.org/search?" + q
    return HttpResponseRedirect(url)


@login_required
def emailshare(request, action):
    if request.method == 'POST':
        form = EmailShareForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = '%s via Unglue.it <%s>' % (request.user.username, request.user.email)
            recipient = form.cleaned_data['recipient']
            send_mail_task.delay(subject, message, sender, [recipient])
            try:
                next = form.cleaned_data['next']
            except:
                # if we totally failed to have a next value, we should still redirect somewhere useful
                next = 'https://unglue.it'
            return HttpResponseRedirect(next)

    else:
        work = None
        status = None

        try:
            next = request.GET['next']
            work_id = next.split('/')[-2]
            work_id = int(work_id)
            work = models.Work.objects.get(pk=work_id)
            if not action:
                status = work.last_campaign().status
        except:
            pass
        context = {'request':request, 'work':work, 'site': Site.objects.get_current(), 'action': action}
        if work and action :
            message = render_to_string('emails/i_just_pledged.txt', context)
            subject = "Help me unglue "+work.title
        else:
            # customize the call to action depending on campaign status
            if status == 'ACTIVE':
                message = render_to_string('emails/pledge_this.txt', context)
                subject = 'Please help me give this book to the world'
            elif work:
                message = render_to_string('emails/wish_this.txt', context)
                subject = 'This is one of my favorite books on Unglue.it'
            else:
                # for email shares not bound to a campaign or pledge
                message = render_to_string('emails/join_me.txt', context)
                subject = "Help me give books to the world"

        form = EmailShareForm(initial={ 'next':next, 'subject': subject, 'message': message})

    return render(request, "emailshare.html", {'form':form})

def ask_rh(request, campaign_id):
    try:
        campaign = get_object_or_404(models.Campaign, id=campaign_id)
    except ValueError:
        raise Http404

    return feedback(request, recipient=campaign.email, template="ask_rh.html",
            message_template="ask_rh.txt",
            redirect_url = reverse('work', args=[campaign.work_id]),
            extra_context={'campaign':campaign, 'subject':campaign })

def feedback(request, recipient='unglueit@ebookfoundation.org', template='feedback.html', message_template='feedback.txt', extra_context=None, redirect_url=None):
    context = extra_context or {}
    context['num1'] = randint(0, 10)
    context['num2'] = randint(0, 10)
    context['answer'] = context['num1'] + context['num2']

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            context.update(form.cleaned_data)
            context['request'] = request
            if extra_context:
                context.update(extra_context)
            message = render_to_string(message_template, context)
            send_mail_task.delay(context['subject'], message, context['sender'], [recipient])
            if redirect_url:
                return HttpResponseRedirect(redirect_url)
            else:
                return render(request, "thanks.html", context)

        else:
            context['num1'] = request.POST['num1']
            context['num2']  = request.POST['num2']

    else:
        if request.user.is_authenticated:
            context['sender'] = request.user.email
        try:
            context['page'] = request.GET['page']
        except:
            context['page'] = '/'
        if not 'subject' in context:
            context['subject'] = "Feedback on page "+context['page']
        form = FeedbackForm(initial=context)
    context['form'] = form
    return render(request, template, context)

def comment(request):
    latest_comments = Comment.objects.all().order_by('-submit_date')[:20]
    return render(request, "comments.html", {'latest_comments': latest_comments})

def campaign_archive_js(request):
    """ proxy for mailchimp js"""
    response = HttpResponse()
    r = requests.get(settings.CAMPAIGN_ARCHIVE_JS)
    response.status_code = r.status_code
    response.content = r.content
    response["Content-Type"] = "text/javascript"
    return response

def lockss(request, work_id):
    """
    manifest pages for lockss harvester -- individual works
    """
    work = safe_get_work(work_id)
    try:
        ebooks = work.ebooks().filter(edition__unglued=True)
    except:
        ebooks = None
    authors = work.authors()

    return render(request, "lockss.html", {'work':work, 'ebooks':ebooks, 'authors':authors})

def lockss_manifest(request, year):
    """
    manifest pages for lockss harvester -- yearly indices
    (lockss needs pages listing all books unglued by year, with
    programmatically determinable URLs)
    """
    year = int(year)
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    try:
        ebooks = models.Edition.objects.filter(unglued=True).filter(created__range=(start_date, end_date))
    except:
        ebooks = None

    return render(request, "lockss_manifest.html", {'ebooks':ebooks, 'year': year})

class DownloadView(PurchaseView):
    template_name = "download.html"
    form_class = CampaignThanksForm
    def show_beg(self):
        if not self.campaign or self.campaign.type != THANKS:
            return  False
        elif self.user_license and self.user_license.thanked:
            return 'offer_id' in self.request.GET or 'offer_id' in self.request.POST
        elif self.lib_thanked:
            return False
        elif self.campaign.status != 'ACTIVE':
            return 'testmode' in self.request.GET or 'testmode' in self.request.POST
        else:
            return True

    def form_valid(self, form):
        p = PaymentManager()
        t, url = p.process_transaction('USD',  form.cleaned_data["preapproval_amount"],
                host = PAYMENT_HOST_NONE,
                campaign = self.campaign,
                user = self.request.user,
                paymentReason="Unglue.it Contribution for {0}".format(self.campaign.name),
                pledge_extra = form.trans_extra,
                )
        if url:
            return HttpResponseRedirect(url)
        else:
            logger.error("Attempt to produce transaction id {0} failed".format(t.id))
            return HttpResponse("Our attempt to set up your contribution failed. We have logged this problem.")

    def get_form_kwargs(self):
        if 'work' in self.kwargs:
            self.work = self.kwargs["work"]
            self.show_beg = lambda: False
        else:
            self.work = safe_get_work(self.kwargs["work_id"])
        self.campaign = self.work.last_campaign()
        self.user_license = self.work.get_user_license(self.request.user)
        self.lib_thanked = self.work.lib_thanked(self.request.user)
        self.data = {
            'preapproval_amount':self.get_preapproval_amount(),
            'anonymous':True if self.request.user.is_anonymous else self.request.user.profile.anon_pref,
            }
        if self.request.method  == 'POST':
            self.data.update(self.request.POST.dict())
            if not 'anonymous' in self.request.POST:
                del self.data['anonymous']
            return {'data':self.data}
        else:
            return {'initial':self.data}

    def get_context_data(self, **kwargs):
        context = super(FormView, self).get_context_data(**kwargs)
        # adapt funtion view to class view
        work =  self.work
        request = self.request
        site = Site.objects.get_current()

        unglued_ebooks = work.ebooks().filter(edition__unglued=True)
        other_ebooks = work.ebooks().filter(edition__unglued=False)
        xfer_url = None
        acq = None
        formats = {}  # a dict of format name and url
        for ebook in work.ebooks().all():
            formats[ebook.format] = reverse('download_ebook', args=[ebook.id])

        if request.user.is_authenticated:
            #add a fave
            request.user.wishlist.add_work(work,'download')

            all_acqs = request.user.acqs.filter(work=work).order_by('-created')
            for an_acq in all_acqs:
                if not an_acq.expired:
                    # skip for THANKS
                    if an_acq.license == THANKED:
                        acq = None
                        break
                    # prepare this acq for download
                    if not an_acq.watermarked or an_acq.watermarked.expired:
                        if not an_acq.on_reserve:
                            watermark_acq.delay(an_acq.id)
                    acq = an_acq
                    formats['epub'] = reverse('download_acq', kwargs={'nonce':acq.nonce, 'format':'epub'})
                    xfer_url = settings.BASE_URL_SECURE + formats['epub']
                    can_kindle = True
                    break


        if not acq:
            # google ebooks have a captcha which breaks some of our services
            non_google_ebooks = work.ebooks().exclude(provider='Google Books')

            #send to kindle

            try:
                kindle_ebook = non_google_ebooks.filter(format='epub')[0]
                can_kindle = kindle_ebook.kindle_sendable()
            except IndexError:
                try:
                    kindle_ebook = non_google_ebooks.filter(format='pdf')[0]
                    can_kindle = kindle_ebook.kindle_sendable()
                except IndexError:
                    can_kindle = False
            # configure the xfer url
            try:
                xfer_epub_ebook = non_google_ebooks.filter(format='epub')[0]
                xfer_url = settings.BASE_URL_SECURE + reverse('download_ebook', args=[xfer_epub_ebook.id])
            except:
                xfer_url = None
        agent = request.META.get('HTTP_USER_AGENT','')
        iOS = 'iPad' in agent or 'iPhone' in agent or 'iPod' in agent
        iOS_app = iOS and not 'Safari' in agent
        android = 'Android' in agent
        desktop = not iOS and not android
        context.update({
            'unglued_ebooks': unglued_ebooks,
            'other_ebooks': other_ebooks,
            'formats': formats,
            'xfer_url': xfer_url,
            'dropbox_key': settings.DROPBOX_KEY,
            'can_kindle': can_kindle,
            'base_url': settings.BASE_URL_SECURE,
            'iOS': iOS,
            'iOS_app': iOS_app,
            'iphone': 'iPhone' in agent,
            'android': android,
            'desktop': desktop,
            'mac_ibooks': 'Mac OS X 10.9' in agent or 'Mac OS X 10_9' in agent or 'Mac OS X 10.10' in agent or 'Mac OS X 10_10' in agent,
            'acq':acq,
            'show_beg': self.show_beg,
            'preapproval_amount': self.get_preapproval_amount(),
            'work': work,
            'site': site,
            'action': "Contribution",
            'user_license': self.user_license,
            'lib_thanked': self.lib_thanked,
            'amount': D(self.request.session.pop('amount') // 100) if 'amount' in self.request.session else None,
            'testmode': 'testmode' in self.request.GET or 'testmode' in self.request.POST,
            'source': self.request.GET.get('source', self.request.POST.get('source', '')),

        })
        return context

@login_required
def feature(request, work_id):
    if not request.user.is_staff:
        return render(request, "admins_only.html")
    else:
        work = safe_get_work(work_id)
        if work.is_free:
            work.featured = now()
            work.save()
            return HttpResponseRedirect(reverse('landing', args=[]))
        else:
            return HttpResponse('can\'t feature an work without an ebook')

@login_required
def borrow(request, work_id):
    work = safe_get_work(work_id)
    library =  request.GET.get('library', '')
    libuser = None
    acq = None
    if library:
        try:
            libuser = User.objects.get(username = library)
        except User.DoesNotExist:
            libuser = None
        if libuser:
            acq = work.get_user_license(libuser).borrowable_acq
    if not libuser or not acq:
        acq = work.get_lib_license(request.user).borrowable_acq
    if acq:
        borrowed = acq.borrow(request.user)
        return DownloadView.as_view()(request, work=work)
    else:
        # shouldn't happen
        return work(request, work_id)

@login_required
def reserve(request, work_id):
    work = safe_get_work(work_id)
    lib =  request.GET.get('library', '')
    library = None
    try:
        library = Library.objects.get(user__username = lib)
    except Library.DoesNotExist:
        try:
            library = work.get_lib_license(request.user).next_acq.library
        except:
            library = None

    models.Hold.objects.get_or_create(library=library, work=work, user=request.user)
    return PurchaseView.as_view()(request, work_id=work_id)

def download_ebook(request, ebook_id):
    try:
        ebook = get_object_or_404(models.Ebook, id=ebook_id)
    except ValueError:
        raise Http404
    ebook.increment()
    logger.info("ebook: {0}, user_ip: {1}".format(ebook_id, request.META['REMOTE_ADDR']))
    return HttpResponseRedirect(ebook.url)

def download_purchased(request, work_id):
    if request.user.is_anonymous:
        HttpResponseRedirect('/accounts/login/download/')
    return DownloadView.as_view()(request, work_id=work_id)

def download_campaign(request, work_id, format):
    work = safe_get_work(work_id)

    # Raise 404 unless there is a SUCCESSFUL BUY2UNGLUE campaign associated with work
    try:
        campaign = work.campaigns.get(status='SUCCESSFUL', type=BUY2UNGLUE)
    except models.Campaign.DoesNotExist as e:
        raise Http404

    ebfs = models.EbookFile.objects.filter(edition__work=campaign.work, format=format).exclude(file='').order_by('-created')
    logger.info(ebfs.count())
    # return the link to the most recently created EbookFile (if any) with specified format for the campaign
    for ebf in ebfs:
        logger.info(ebf.file.url)
        return HttpResponseRedirect(ebf.file.url)

    # if ebfs.count() is 0
    raise Http404

def download_acq(request, nonce, format):
    acq = get_object_or_404(models.Acq, nonce=nonce)
    if acq.on_reserve:
        acq.borrow()
    if format == 'epub':
        return HttpResponseRedirect(acq.get_epub_url())

def about(request, facet):
    template = "about_" + facet + ".html"
    try:
        return render(request, template)
    except TemplateDoesNotExist:
        return render(request, "about_main.html")

def receive_gift(request, nonce):
    try:
        gift = models.Gift.objects.get(acq__nonce=nonce)
    except models.Gift.DoesNotExist:
        return render(request, 'gift_error.html',)
    context = {'gift': gift, "site": Site.objects.get_current() }
    work = gift.acq.work
    context['work'] = work
    # put nonce in session so we know that a user has redeemed a Gift
    request.session['gift_nonce'] = nonce
    if gift.used:
        if request.user.is_authenticated:
            #check that user hasn't redeemed the gift themselves
            if (gift.acq.user_id == request.user.id) and not gift.acq.expired:
                return HttpResponseRedirect(reverse('display_gift', args=[gift.id,'existing']))
        return render(request, 'gift_error.html', context)
    if request.user.is_authenticated:
        user_license = work.get_user_license(request.user)
        if user_license and user_license.purchased:
            # check if previously purchased- there would be two user licenses if so.
            if user_license.is_duplicate or request.user.id == gift.giver.id:
                # regift
                if request.method == 'POST':
                    form = RegiftForm(data=request.POST)
                    if form.is_valid():
                        giftee = models.Gift.giftee(form.cleaned_data['give_to'], request.user.username)
                        new_acq = models.Acq.objects.create(user=giftee, work=gift.acq.work, license= gift.acq.license)
                        new_gift = models.Gift.objects.create(acq=new_acq, message=form.cleaned_data['give_message'], giver=request.user , to = form.cleaned_data['give_to'])
                        context['gift'] = new_gift
                        gift.acq.expire_in(0)
                        gift.use()
                        notification.send([giftee], "purchase_gift", context, True)
                        from regluit.core.tasks import emit_notifications
                        emit_notifications.delay()
                        return render(request, 'gift_duplicate.html', context)
                context['form'] = RegiftForm()
                return render(request, 'gift_duplicate.html', context)
            else:
                # new book!
                gift.use()
                request.user.wishlist.add_work(gift.acq.work, 'gift')
                return HttpResponseRedirect(reverse('display_gift', args=[gift.id,'existing']))
        else:
            # we'll just leave the old user inactive.
            gift.acq.user = request.user
            gift.acq.save()
            gift.use()
            request.user.wishlist.add_work(gift.acq.work, 'gift')
            return HttpResponseRedirect(reverse('display_gift', args=[gift.id,'existing']))
    if (gift.acq.created - gift.acq.user.date_joined) > timedelta(minutes=1) or gift.used:
        # giftee is established user (or gift has been used), ask them to log in
        return superlogin(request, extra_context=context, template_name='gift_login.html')
    else:
        # giftee is a new user, log them in
        gift.use()
        gift.acq.user.wishlist.add_work(gift.acq.work, 'gift')
        login_user(request, gift.acq.user)

        return HttpResponseRedirect(reverse('display_gift', args=[gift.id, 'newuser']))

@login_required
def display_gift(request, gift_id, message):
    try:
        gift = models.Gift.objects.get(id=gift_id)
    except models.Gift.DoesNotExist:
        return render(request, 'gift_error.html',)
    if request.user.id != gift.acq.user_id :
        return HttpResponse("this is not your gift")
    redeemed_gift =  request.session.get('gift_nonce', None) == gift.acq.nonce
    context = {'gift': gift, 'work': gift.acq.work , 'message':message }
    if request.method == 'POST' and redeemed_gift:
        form = UserNamePass(data=request.POST)
        form.oldusername = request.user.username
        context['form'] = form
        if form.is_valid():
            request.user.username = form.cleaned_data['username']
            request.user.set_password(form.cleaned_data['password1'])
            request.user.save()
            context.pop('form')
            context['passmessage'] = "changed userpass"
        return render(request, 'gift_welcome.html', context)
    else:
        if redeemed_gift:
            form = UserNamePass(initial={'username':request.user.username})
            form.oldusername = request.user.username
            context['form'] = form
        return render(request, 'gift_welcome.html', context)

@login_required
@csrf_exempt
def ml_status(request):
    return render(request, "ml_status.html")

@require_POST
@login_required
def ml_subscribe(request):
    request.user.profile.ml_subscribe(
        double_optin=False,
        send_welcome=True,
        merge_vars = {"OPTIN_IP":request.META['REMOTE_ADDR'], "OPTIN_TIME":now().isoformat()}
    )
    return HttpResponseRedirect(reverse("notification_notice_settings"))

@require_POST
@login_required
def ml_unsubscribe(request):
    request.user.profile.ml_unsubscribe()
    return HttpResponseRedirect(reverse("notification_notice_settings"))

def press(request):
    latest_items = models.Press.objects.order_by('-date')[:3]
    highlighted_items = models.Press.objects.filter(highlight=True).order_by('-date')
    all_items = models.Press.objects.exclude(highlight=True).order_by('-date')
    return render(request, "press_new.html", {
        'latest_items': latest_items,
        'highlighted_items': highlighted_items,
        'all_items': all_items
    })

def press_submitterator(request):
    if not request.user.is_staff:
        return render(request, "admins_only.html")
    else:
        title = ''
        if request.method == 'POST':
            form = PressForm(request.POST)
            if form.is_valid():
                form.save()
                title = form.cleaned_data['title']
        else:
            form = PressForm()

        return render(request, 'press_submitterator.html', {
            'form':form,
            'title':title
        })

@login_required
def kindle_config(request, work_id=None):
    if work_id:
        work = safe_get_work(work_id)
    else:
        work = None
    template = "kindle_config.html"
    if request.method == 'POST':
        form = KindleEmailForm(request.POST)
        if form.is_valid():
            request.user.profile.kindle_email = form.cleaned_data['kindle_email']
            request.user.profile.save()
            template = "kindle_change_successful.html"
    else:
        form = KindleEmailForm()
    return render(request, template, {
            'form': form,
            'work': work,
            'ok_email': request.user.profile.kindle_email and ('kindle' in request.user.profile.kindle_email),
        })

@require_POST
@csrf_exempt
def send_to_kindle(request, work_id, javascript='0'):

    # make sure to gracefully communicate with both js and non-js (kindle!) users
    def local_response(request, javascript, context, message):
        context['message'] = message
        if javascript == '1':
            return render(request, 'kindle_response_message.html', context)
        else:
            return render(request, 'kindle_response_graceful_degradation.html', context)

    work = safe_get_work(work_id)
    context = {'work':work}
    acq = None
    if request.user.is_authenticated:
        all_acqs = request.user.acqs.filter(work=work).order_by('-created')
        for an_acq in all_acqs:
            if not an_acq.expired:
                # skip for THANKS
                if an_acq.license == THANKED:
                    acq = None
                    break
                # prepare this acq for download
                if not an_acq.watermarked or an_acq.watermarked.expired:
                    if not an_acq.on_reserve:
                        watermark_acq.delay(an_acq.id)
                acq = an_acq
                break

    if acq:
        ebook = acq.ebook()
        title = acq.work.kindle_safe_title()
    else:
        non_google_ebooks = work.ebooks().exclude(provider='Google Books')
        try:
            ebook = non_google_ebooks.filter(format='epub')[0]
        except IndexError:
            try:
                ebook = non_google_ebooks.filter(format='pdf')[0]
            except IndexError:
                raise Http404

        # don't forget to increment the download counter!
        ebook.increment()
        logger.info('ebook: {0}, user_ip: {1}'.format(work_id, request.META['REMOTE_ADDR']))
        title = ebook.edition.work.kindle_safe_title()
    context['ebook'] = ebook

    if 'kindle_email' in request.POST:
        kindle_email = request.POST['kindle_email']
        try:
            validate_email(kindle_email)
        except ValidationError:
            return local_response(request, javascript,  context, 3)
        request.session['kindle_email'] = kindle_email
    elif request.user.is_authenticated:
        kindle_email = request.user.profile.kindle_email
    context['kindle_email'] = kindle_email


    """
    Amazon SES has a 10 MB size limit (https://aws.amazon.com/ses/faqs/#49) in messages sent
    to determine whether the file will meet this limit, we probably need to compare the
    size of the mime-encoded file to 10 MB. (and it's unclear exactly what the Amazon FAQ means precisely by
    MB either: https://en.wikipedia.org/wiki/Megabyte) http://www.velocityreviews.com/forums/t335208-how-to-get-size-of-email-attachment.html might help

    for the moment, we will hardwire a 749229 limit in filesize:
    * assume conservative size of megabyte, 1000000B
    * leave 1KB for headers
    * mime encoding will add 33% to filesize
    This won't perfectly measure size of email, but should be safe, and is much faster than doing the check after download.
    """
    try:
        filehandle = ebook.get_archive()
    except IOError:
        # problems connection to the ebook source
        logger.error("couldn't connect error: %s", ebook.url)
        return local_response(request, javascript,  context, 5)
    if not ebook.filesize:
        return local_response(request, javascript,  context, 4)
    if ebook.filesize > models.send_to_kindle_limit:
        logger.info('ebook %s is too large to be emailed' % work.id)
        return local_response(request, javascript,  context, 0)

    try:
        email = EmailMessage(from_email='notices@gluejar.com',
                to=[kindle_email])
        email.attach(title + '.' + ebook.format, filehandle.read())
        email.send()
    except:
        logger.error('Unexpected error: %s', sys.exc_info())
        return local_response(request, javascript,  context, 1)

    if 'kindle_email' in request.POST and not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('superlogin'))
    return local_response(request, javascript,  context, 2)


def userlist_marc(request, userlist=None):
    if userlist:
        user = get_object_or_404(User, username=userlist)
        return qs_marc_records(request, qs=user.wishlist.works.all())
    else:
        return qs_marc_records(request, qs=request.user.wishlist.works.all())

    return render(request, 'marc.html', {'userlist' : [] })

def work_marc(request, work_id):
    work = safe_get_work(work_id)
    return qs_marc_records(request, qs=[ work ])


class LibModeView(FormView):
    template_name = 'marc_config.html'
    form_class = LibModeForm
    success_url = reverse_lazy('marc')

    def form_valid(self, form):
        enable = 'enable' in form.data
        if enable:
            try:
                libpref = self.request.user.libpref
            except:
                libpref = models.Libpref(user=self.request.user)
            libpref.save()
            messages.success(self.request,"Tools are enabled.")
        else:
            try:
                self.request.user.libpref.delete()
            except:
                pass
            messages.success(self.request,"Tools are disabled.")
        if reverse('marc_config', args=[]) in self.request.META['HTTP_REFERER']:
            return HttpResponseRedirect(reverse('marc_config', args=[]))
        else:
            return super(LibModeView, self).form_valid(form)



