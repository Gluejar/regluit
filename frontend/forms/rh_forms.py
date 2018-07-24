from datetime import date, timedelta
from decimal import Decimal as D

from ckeditor_uploader.widgets import CKEditorUploadingWidget

from selectable.forms import (
    AutoCompleteSelectMultipleWidget,
    AutoCompleteSelectMultipleField,
)

from django import forms
from django.conf import settings
from django.forms.widgets import RadioSelect, SelectDateWidget
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from regluit.core.lookups import OwnerLookup
from regluit.core.models import Campaign, Edition, Claim, RightsHolder, WasWork
from regluit.core.parameters import *

class RightsHolderForm(forms.ModelForm):
    email = forms.EmailField(
        help_text='notification email address for rights holder',
        max_length=100,
        error_messages={
                'required': 'Please enter a contact email address for the rights holder.'
            },
    )
    use4both = forms.BooleanField(label='use business address as mailing address', required=False)
    def clean_rights_holder_name(self):
        rights_holder_name = self.data["rights_holder_name"]
        try:
            RightsHolder.objects.get(rights_holder_name__iexact=rights_holder_name)
        except RightsHolder.DoesNotExist:
            return rights_holder_name
        raise forms.ValidationError('Another rights holder with that name already exists.')

    class Meta:
        model = RightsHolder
        exclude = ('approved', 'signer_ip')
        widgets = {
            'address': forms.Textarea(attrs={'rows': 4}),
            'mailing': forms.Textarea(attrs={'rows': 4}),
            'owner': forms.HiddenInput()
        }
        help_texts = {
            'signature': 'Type your name to enter your electronic signature.',
            'rights_holder_name':  'Enter the rights holder\'s legal name.',
        }
        error_messages = {
            'address': {
                'required': 'A business address for the rights holder is required.'
                },
            'mailing': {
                'required': 'Enter a mailing address for the rights holder, if different from the \
                             business address.'
            },
            'rights_holder_name': {
                'required': 'Enter the rights holder\'s legal name.'
            },
            'signature': {
                'required': 'Type your name to enter your electronic signature.'
            },
            'signer': {
                'required': 'Please enter the name of the person signing on behalf of the rights \
                             holder.'
            },
            'signer_title': {
                'required': 'Please enter the signer\'s title. (Use \'self\' if you are \
                             personally the rights holder.)'
            },
        }

class UserClaimForm (forms.ModelForm):
    i_agree = forms.BooleanField(
            error_messages={'required': 'You must agree to the Terms in order to claim a work.'}
        )

    def __init__(self, user_instance, *args, **kwargs):
        super(UserClaimForm, self).__init__(*args, **kwargs)
        self.fields['rights_holder'] = forms.ModelChoiceField(
            queryset=user_instance.rights_holder.all(),
            empty_label=None,
        )

    def clean_work(self):
        work = self.cleaned_data.get('work', None)
        if not work:
            try:
                workids = self.data['claim-work']
                if workids:
                    work = WasWork.objects.get(was = workids[0]).work
                else:
                    raise forms.ValidationError('That work does not exist.')
            except WasWork.DoesNotExist:
                raise forms.ValidationError('That work does not exist.')
        return work

    class Meta:
        model = Claim
        exclude = ('status',)
        widgets = {
                'user': forms.HiddenInput,
                'work': forms.HiddenInput,
        }

class EditManagersForm(forms.ModelForm):
    managers = AutoCompleteSelectMultipleField(
            OwnerLookup,
            label='Campaign Managers',
            widget=AutoCompleteSelectMultipleWidget(OwnerLookup),
            required=True,
            error_messages = {'required': "You must have at least one manager for a campaign."},
        )
    class Meta:
        model = Campaign
        fields = ('id', 'managers')
        widgets = { 'id': forms.HiddenInput }

class OpenCampaignForm(forms.ModelForm):
    managers = AutoCompleteSelectMultipleField(
            OwnerLookup,
            label='Campaign Managers',
            widget=AutoCompleteSelectMultipleWidget(OwnerLookup),
            required=True,
            error_messages = {'required': "You must have at least one manager for a campaign."},
        )
    userid = forms.IntegerField( required = True, widget = forms.HiddenInput )
    class Meta:
        model = Campaign
        fields = 'name', 'work',  'managers', 'type'
        widgets = { 'work': forms.HiddenInput, "name": forms.HiddenInput, }

class CloneCampaignForm(forms.Form):
    campaign_id = forms.IntegerField(required = True, widget = forms.HiddenInput)

date_selector = range(date.today().year, settings.MAX_CC_DATE.year+1)

class CCDateForm(object):
    target = forms.DecimalField(
        min_value= D(settings.UNGLUEIT_MINIMUM_TARGET),
        error_messages={'required': 'Please specify a Revenue Target.'}
    )
    minimum_target = settings.UNGLUEIT_MINIMUM_TARGET
    maximum_target = settings.UNGLUEIT_MAXIMUM_TARGET
    max_cc_date = settings.MAX_CC_DATE

    def clean_target(self):
        new_target = self.cleaned_data['target']
        if new_target < D(settings.UNGLUEIT_MINIMUM_TARGET):
            raise forms.ValidationError(_(
                'A campaign may not be launched with a target less than $%s' % settings.UNGLUEIT_MINIMUM_TARGET
            ))
        if new_target > D(settings.UNGLUEIT_MAXIMUM_TARGET):
            raise forms.ValidationError(_(
                'A campaign may not be launched with a target more than $%s' % settings.UNGLUEIT_MAXIMUM_TARGET
            ))
        return new_target

    def clean_cc_date_initial(self):
        new_cc_date_initial = self.cleaned_data['cc_date_initial']
        if new_cc_date_initial.date() > settings.MAX_CC_DATE:
            raise forms.ValidationError('The initial Ungluing Date cannot be after %s'%settings.MAX_CC_DATE)
        elif new_cc_date_initial - now() < timedelta(days=0):
            raise forms.ValidationError('The initial Ungluing date must be in the future!')
        return new_cc_date_initial

class DateCalculatorForm(CCDateForm, forms.ModelForm):
    revenue = forms.DecimalField()
    cc_date_initial = forms.DateTimeField(
            widget = SelectDateWidget(years=date_selector)
        )
    class Meta:
        model = Campaign
        fields = 'target',  'cc_date_initial', 'revenue',


class ManageCampaignForm(CCDateForm, forms.ModelForm):
    def __init__(self, instance=None , **kwargs):
        super(ManageCampaignForm, self).__init__(instance=instance, **kwargs)
        work = instance.work
        edition_qs = Edition.objects.filter(work=work)
        self.fields['edition'] = forms.ModelChoiceField(
            edition_qs,
            widget=RadioSelect(),
            empty_label='no edition selected',
            required=False,
        )
        self.fields['target'] = forms.DecimalField(
            required=(instance.type in {REWARDS, BUY2UNGLUE})
        )
        self.fields['deadline'] = forms.DateTimeField(
            required = (instance.type==REWARDS),
            widget = SelectDateWidget(years=date_selector) if instance.status=='INITIALIZED' \
                else forms.HiddenInput
        )
        self.fields['cc_date_initial'] = forms.DateTimeField(
            required = (instance.type==BUY2UNGLUE) and instance.status=='INITIALIZED',
            widget = SelectDateWidget(years=date_selector) if instance.status=='INITIALIZED' \
                else forms.HiddenInput
        )
        self.fields['publisher'] = forms.ModelChoiceField(
            instance.work.publishers(),
            empty_label='no publisher selected',
            required=False,
        )
        if self.initial and not self.initial.get('edition', None) and not instance.edition:
            self.initial['edition'] = instance.work.editions.all()[0]

    paypal_receiver = forms.EmailField(
        label=_("contact email address for this campaign"),
        max_length=100,
        error_messages={
            'required': 'You must enter the email we should contact you at for this campaign.'
            },
        )
    work_description = forms.CharField(required=False , widget=CKEditorUploadingWidget())

    class Meta:
        model = Campaign
        fields = ('description', 'details', 'license', 'target', 'deadline', 'paypal_receiver',
            'edition', 'email', 'publisher',  'cc_date_initial', "do_watermark", "use_add_ask",
        )
        widgets = { 'deadline': SelectDateWidget }

    def clean_target(self):
        if self.instance.type == THANKS:
            return None
        new_target = super(ManageCampaignForm, self).clean_target()
        if self.instance:
            if self.instance.status == 'ACTIVE' and self.instance.target < new_target:
                raise forms.ValidationError(
                    _('The fundraising target for an ACTIVE campaign cannot be increased.')
                )
        return new_target

    def clean_cc_date_initial(self):
        if self.instance.type in {REWARDS, THANKS} :
            return None
        if self.instance:
            if self.instance.status != 'INITIALIZED':
                # can't change this once launched
                return self.instance.cc_date_initial
        return super(ManageCampaignForm, self).clean_cc_date_initial()

    def clean_deadline(self):
        if self.instance.type in {BUY2UNGLUE, THANKS} :
            return None
        new_deadline_date = self.cleaned_data['deadline']
        new_deadline = new_deadline_date + timedelta(hours=23, minutes=59)
        if self.instance:
            if self.instance.status == 'ACTIVE':
                return self.instance.deadline
        if new_deadline_date - now() > timedelta(days=int(settings.UNGLUEIT_LONGEST_DEADLINE)):
            raise forms.ValidationError(_(
                'The chosen closing date is more than {} days from now'.format(
                    settings.UNGLUEIT_LONGEST_DEADLINE
                )
            ))
        elif new_deadline - now() < timedelta(days=0):
            raise forms.ValidationError(_('The chosen closing date is in the past'))
        return new_deadline

    def clean_license(self):
        NO_ADDED_RESTRICTIONS = _(
                        'The proposed license for an ACTIVE campaign may not add restrictions.'
            )
        new_license = self.cleaned_data['license']
        if self.instance:
            if self.instance.status == 'ACTIVE' and self.instance.license != new_license:
                # should only allow change to a less restrictive license
                if self.instance.license == 'CC BY-ND' and new_license in [
                    'CC BY-NC-ND',
                    'CC BY-NC-SA',
                    'CC BY-NC'
                ]:
                    raise forms.ValidationError(NO_ADDED_RESTRICTIONS)
                elif self.instance.license == 'CC BY' and new_license != 'CC0':
                    raise forms.ValidationError(NO_ADDED_RESTRICTIONS)
                elif self.instance.license == 'CC BY-NC' and new_license in [
                    'CC BY-NC-ND',
                    'CC BY-NC-SA',
                    'CC BY-SA',
                    'CC BY-ND'
                ]:
                    raise forms.ValidationError(NO_ADDED_RESTRICTIONS)
                elif self.instance.license == 'CC BY-ND' and new_license in [
                    'CC BY-NC-ND',
                    'CC BY-NC-SA',
                    'CC BY-SA',
                    'CC BY-NC'
                ]:
                    raise forms.ValidationError(NO_ADDED_RESTRICTIONS)
                elif self.instance.license == 'CC BY-SA' and new_license in [
                    'CC BY-NC-ND',
                    'CC BY-NC-SA',
                    'CC BY-ND',
                    'CC BY-NC'
                ]:
                    raise forms.ValidationError(NO_ADDED_RESTRICTIONS)
                elif self.instance.license == 'CC BY-NC-SA' and new_license in [
                    'CC BY-NC-ND',
                    'CC BY-ND'
                ]:
                    raise forms.ValidationError(NO_ADDED_RESTRICTIONS)
                elif self.instance.license == 'CC0' :
                    raise forms.ValidationError(NO_ADDED_RESTRICTIONS)
                elif self.instance.license in ['GDFL', 'LAL']:
                    raise forms.ValidationError(_(
                        'Once you start a campaign with GDFL or LAL, you can\'t use any other license.'
                    ))
        return new_license


