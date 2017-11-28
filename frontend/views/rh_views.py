from datetime import timedelta
from decimal import Decimal as D

from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.views.generic.edit import CreateView

from regluit.core import models
from regluit.core.parameters import *
from regluit.frontend.forms import (
    CloneCampaignForm,
    EditManagersForm,
    OpenCampaignForm,
    RightsHolderForm,
    UserClaimForm,
)
from regluit.utils.localdatetime import date_today

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
    if not request.user.is_authenticated() or not request.user.is_staff:
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
    if user.is_anonymous():
        return False
    for rh in user.rights_holder.filter(approved=True):
        return True
    return False

class ClaimView(CreateView):
    template_name = "claim.html"
    def get_form(self):
        return UserClaimForm(self.request.user, data=self.request.POST, prefix='claim')

    def form_valid(self, form):
        print form.cleaned_data
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

    def get_context_data(self, form):
        work = form.cleaned_data['work']
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
    if not request.user.is_authenticated() :
        return render(request, "rh_tools.html")
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

