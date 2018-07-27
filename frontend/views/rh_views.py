from datetime import timedelta
from decimal import Decimal as D
import logging

from django.conf import settings
from django.urls import reverse, reverse_lazy
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView
from django.utils.translation import ugettext_lazy as _

from regluit.core import models, tasks
from regluit.core.parameters import *
from regluit.frontend.forms import (
    CloneCampaignForm,
    CustomPremiumForm,
    EditManagersForm,
    ManageCampaignForm,
    OpenCampaignForm,
    OfferForm,
    RightsHolderForm,
    UserClaimForm,
)
from regluit.utils.localdatetime import date_today

logger = logging.getLogger(__name__)

class RHAgree(CreateView):
    template_name = "rh_agree.html"
    form_class = RightsHolderForm
    success_url = reverse_lazy('agreed')

    def get_initial(self):
        return {'owner':self.request.user.id, 'signature':''}

    def form_valid(self, form):
        form.instance.signer_ip = self.request.META['REMOTE_ADDR']
        return super(RHAgree, self).form_valid(form)

def rh_admin(request, facet='top'):
    if not request.user.is_authenticated or not request.user.is_staff:
        return render(request, "admins_only.html")

    PendingFormSet = modelformset_factory(models.RightsHolder, fields=['approved'], extra=0)
    pending_data = models.RightsHolder.objects.filter(approved=False)

    if  request.method == 'POST':
        if 'approve_rights_holder' in request.POST.keys():
            pending_formset = PendingFormSet (request.POST, request.FILES, queryset=pending_data)
            if pending_formset.is_valid():
                pending_formset.save()
                pending_formset = PendingFormSet(queryset=pending_data)
    else:
        pending_formset = PendingFormSet(queryset=pending_data)

    rights_holders = models.RightsHolder.objects.filter(approved=True)

    context = {
        'rights_holders': rights_holders,
        'pending': zip(pending_data, pending_formset),
        'pending_formset': pending_formset,
        'facet': facet,
    }
    return render(request, "rights_holders.html", context)

def user_is_rh(user):
    if user.is_anonymous:
        return False
    for rh in user.rights_holder.filter(approved=True):
        return True
    return False

class ClaimView(CreateView):
    template_name = "claim.html"
    def get_form(self):
        return UserClaimForm(self.request.user, data=self.request.POST, prefix='claim')

    def form_valid(self, form):
        logger.info(form.cleaned_data)
        work = form.cleaned_data['work']
        rights_holder = form.cleaned_data['rights_holder']
        if not rights_holder.approved:
            form.instance.status = 'pending'
        # make sure we're not creating a duplicate claim
        if not models.Claim.objects.filter(
            work=work,
            rights_holder=rights_holder,
        ).exclude(status='release').count():
            form.save()
        return HttpResponseRedirect(reverse('rightsholders'))

    def get_context_data(self, form=None):
        try:
            work = form.cleaned_data['work']
        except AttributeError:
            return {}
        rights_holder = form.cleaned_data['rights_holder']
        active_claims = work.claim.exclude(status = 'release')
        return {
            'form': form,
            'work': work,
            'rights_holder': rights_holder,
            'active_claims': active_claims,
        }

def claim(request):
    return ClaimView.as_view()(request)

def rh_tools(request, template_name='rh_intro.html'):
    if not request.user.is_authenticated:
        return render(request, 'rh_intro.html')
    claims = request.user.claim.filter(user=request.user)
    campaign_form = "xxx"
    if not claims:
        return render(request, template_name)
    for claim in claims:
        if claim.can_open_new:
            if request.method == 'POST' and  \
                    request.POST.has_key('cl_%s-work' % claim.id) and \
                    int(request.POST['cl_%s-work' % claim.id]) == claim.work_id :
                claim.campaign_form = OpenCampaignForm(
                    data = request.POST,
                    prefix = 'cl_'+str(claim.id),
                )
                if claim.campaign_form.is_valid():
                    new_campaign = claim.campaign_form.save(commit=False)
                    if new_campaign.type == BUY2UNGLUE:
                        new_campaign.target = D(settings.UNGLUEIT_MAXIMUM_TARGET)
                        new_campaign.set_cc_date_initial()
                    elif new_campaign.type == REWARDS:
                        new_campaign.deadline = date_today() + timedelta(
                            days=int(settings.UNGLUEIT_LONGEST_DEADLINE)
                        )
                        new_campaign.target = D(settings.UNGLUEIT_MINIMUM_TARGET)
                    elif new_campaign.type == THANKS:
                        new_campaign.target = D(settings.UNGLUEIT_MINIMUM_TARGET)
                    new_campaign.save()
                    claim.campaign_form.save_m2m()
                    claim.campaign_form = None
            else:
                c_type = 2
                claim.campaign_form = OpenCampaignForm(
                    initial={
                        'work': claim.work,
                        'name': claim.work.title,
                        'userid': request.user.id,
                        'managers': [request.user.id],
                        'type': c_type
                    },
                    prefix='cl_'+str(claim.id),
                    )
        if claim.campaign:
            if claim.campaign.status in ['ACTIVE','INITIALIZED']:
                e_m_key = 'edit_managers_%s' % claim.campaign.id
                if request.method == 'POST' and request.POST.has_key(e_m_key):
                    claim.campaign.edit_managers_form = EditManagersForm(
                        instance=claim.campaign,
                        data=request.POST,
                        prefix=claim.campaign.id,
                    )
                    if claim.campaign.edit_managers_form.is_valid():
                        claim.campaign.edit_managers_form.save()
                        claim.campaign.edit_managers_form = EditManagersForm(
                            instance=claim.campaign,
                            prefix=claim.campaign.id,
                        )
                else:
                    claim.campaign.edit_managers_form = EditManagersForm(
                        instance=claim.campaign,
                        prefix=claim.campaign.id,
                    )
    campaigns = request.user.campaigns.all()
    new_campaign = None
    for campaign in campaigns:
        if campaign.clonable():
            if request.method == 'POST' and  request.POST.has_key('c%s-campaign_id'% campaign.id):
                clone_form = CloneCampaignForm(data=request.POST, prefix = 'c%s' % campaign.id)
                if clone_form.is_valid():
                    campaign.clone()
            else:
                campaign.clone_form = CloneCampaignForm(
                    initial={'campaign_id':campaign.id},
                    prefix='c%s' % campaign.id,
                )
    return render(request, template_name, {'claims': claims , 'campaigns': campaigns})

def campaign_results(request, campaign):
    return render(request, 'campaign_results.html', {
            'campaign': campaign,
        })

def manage_campaign(request, id, ebf=None, action='manage'):
    try:
        campaign = get_object_or_404(models.Campaign, id=id)
    except ValueError:
        raise Http404
    
    campaign.not_manager = False
    campaign.problems = []
    if (not request.user.is_authenticated) or \
            (not request.user in campaign.managers.all() and not request.user.is_staff):
        campaign.not_manager = True
        return render(request, 'manage_campaign.html', {'campaign': campaign})
    if action == 'results':
        return campaign_results(request, campaign)
    alerts = []
    activetab = '#1'
    offers = campaign.work.offers.all()
    for offer in offers:
        offer.offer_form = OfferForm(instance=offer, prefix='offer_%d'%offer.id)

    if request.method == 'POST' :
        if request.POST.has_key('add_premium') :
            new_premium_form = CustomPremiumForm(data=request.POST)
            if new_premium_form.is_valid():
                new_premium_form.save()
                alerts.append(_('New premium has been added'))
                new_premium_form = CustomPremiumForm(initial={'campaign': campaign})
            else:
                alerts.append(_('New premium has not been added'))
            form = ManageCampaignForm(instance=campaign)
            activetab = '#2'
        elif request.POST.has_key('save') or request.POST.has_key('launch') :
            form = ManageCampaignForm(instance=campaign, data=request.POST)
            if form.is_valid():
                form.save()
                campaign.dollar_per_day = None
                campaign.set_dollar_per_day()
                campaign.work.selected_edition = campaign.edition
                if campaign.type in {BUY2UNGLUE, THANKS} :
                    offers = campaign.work.create_offers()
                    for offer in offers:
                        offer.offer_form = OfferForm(instance=offer, prefix='offer_%d'%offer.id)
                campaign.update_left()
                if campaign.type is THANKS :
                    campaign.work.description = form.cleaned_data['work_description']
                    tasks.process_ebfs.delay(campaign)
                campaign.work.save()
                alerts.append(_('Campaign data has been saved'))
                activetab = '#2'
            else:
                alerts.append(_('Campaign data has NOT been saved'))
            if 'launch' in request.POST.keys():
                activetab = '#3'
                if (campaign.launchable and form.is_valid()) and \
                        (not settings.IS_PREVIEW or request.user.is_staff):
                    campaign.activate()
                    alerts.append(_('Campaign has been launched'))
                else:
                    alerts.append(_('Campaign has NOT been launched'))
            new_premium_form = CustomPremiumForm(initial={'campaign': campaign})
        elif request.POST.has_key('inactivate') :
            activetab = '#2'
            if request.POST.has_key('premium_id'):
                premiums_to_stop = request.POST.getlist('premium_id')
                for premium_to_stop in premiums_to_stop:
                    selected_premium = models.Premium.objects.get(id=premium_to_stop)
                    if selected_premium.type == 'CU':
                        selected_premium.type = 'XX'
                        selected_premium.save()
                        alerts.append(_('Premium %s has been inactivated'% premium_to_stop))
            form = ManageCampaignForm(instance=campaign)
            new_premium_form = CustomPremiumForm(initial={'campaign': campaign})
        elif request.POST.has_key('change_offer'):
            for offer in offers :
                if request.POST.has_key('offer_%d-work' % offer.id) :
                    offer.offer_form = OfferForm(
                        instance=offer,
                        data = request.POST,
                        prefix='offer_%d'%offer.id
                    )
                    if offer.offer_form.is_valid():
                        offer.offer_form.save()
                        offer.active =  True
                        offer.save()
                        alerts.append(_('Offer has been changed'))
                    else:
                        alerts.append(_('Offer has not been changed'))
            form = ManageCampaignForm(instance=campaign)
            new_premium_form = CustomPremiumForm(data={'campaign': campaign})
            activetab = '#2'
    else:
        if action == 'makemobi':
            try:
                ebookfile = get_object_or_404(models.EbookFile, id=ebf)
            except ValueError:
                raise Http404

            tasks.make_mobi.delay(ebookfile)
            return HttpResponseRedirect(reverse('mademobi', args=[campaign.id]))
        elif action == 'mademobi':
            alerts.append('A MOBI file is being generated')
        form = ManageCampaignForm(
            instance=campaign,
            initial={'work_description':campaign.work.description}
        )
        new_premium_form = CustomPremiumForm(initial={'campaign': campaign})

    return render(request, 'manage_campaign.html', {
        'campaign': campaign,
        'form':form,
        'problems': campaign.problems,
        'alerts': alerts,
        'premiums' : campaign.custom_premiums(),
        'premium_form' : new_premium_form,
        'work': campaign.work,
        'activetab': activetab,
        'offers':offers,
        'action':action,
    })
