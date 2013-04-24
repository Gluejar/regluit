from datetime import timedelta
from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from django.conf.global_settings import LANGUAGES
from django.core.validators import validate_email
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import RadioSelect
from django.forms.extras.widgets import SelectDateWidget

from decimal import Decimal as D
from selectable.forms import AutoCompleteSelectMultipleWidget,AutoCompleteSelectMultipleField
from selectable.forms import AutoCompleteSelectWidget,AutoCompleteSelectField

from regluit.core.models import UserProfile, RightsHolder, Claim, Campaign, Premium, Ebook, Edition, PledgeExtra, Work, Press
from regluit.core.models import TWITTER, FACEBOOK, GRAVATAR
from regluit.core.lookups import OwnerLookup, WorkLookup, PublisherNameLookup

from regluit.utils.localdatetime import now

import logging

logger = logging.getLogger(__name__)

class EditionForm(forms.ModelForm):
    add_author = forms.CharField(max_length=500,  required=False)
    add_subject = forms.CharField(max_length=200,  required=False)
    publisher_name = AutoCompleteSelectField(
            PublisherNameLookup,
            label='Publisher Name',
            widget=AutoCompleteSelectWidget(PublisherNameLookup),
            required=False,
        )

    isbn = forms.RegexField(
        label=_("ISBN"), 
        max_length=13, 
        regex=r'^(97[89]\d\d\d\d\d\d\d\d\d\d|delete)$',
        required = True,
        help_text = _("13 digits, no dash."),
        error_messages = {
            'invalid': _("This value must be 13 digits, starting with 978 or 979."),
            'required': _("Yes, we need an ISBN."),
        }
    )
    goog = forms.RegexField(
        label=_("Google Books ID"), 
        max_length=12, 
        regex=r'^([a-zA-Z0-9\-_]{12}|delete)$',
        required = False,
        help_text = _("12 alphanumeric characters, dash or underscore, case sensitive."),
        error_messages = {
            'invalid': _("This value must be 12 alphanumeric characters, dash or underscore."),
        }
    )
    gdrd = forms.RegexField(
        label=_("GoodReads ID"), 
        max_length=8, 
        regex=r'^(\d+|delete)$',
        required = False,
        help_text = _("1-8 digits."),
        error_messages = {
            'invalid': _("This value must be 1-8 digits."),
        }
    )
    thng = forms.RegexField(
        label=_("LibraryThing ID"), 
        max_length=8, 
        regex=r'(^\d+|delete)$',
        required = False,
        help_text = _("1-8 digits."),
        error_messages = {
            'invalid': _("This value must be 1-8 digits."),
        }
    )
    oclc = forms.RegexField(
        label=_("OCLCnum"), 
        regex=r'^(\d\d\d\d\d\d\d\d\d*|delete)$',
        required = False,
        help_text = _("8 or more digits."),
        error_messages = {
            'invalid': _("This value must be 8 or more digits."),
        }
    )
    language = forms.ChoiceField(choices=LANGUAGES)
    description = forms.CharField( required=False, widget= forms.Textarea(attrs={'cols': 80, 'rows': 2}))
    class Meta:
        model = Edition
        exclude = 'created', 'work'
        widgets = { 
                'title': forms.TextInput(attrs={'size': 40}),
                'add_author': forms.TextInput(attrs={'size': 30}),
                'add_subject': forms.TextInput(attrs={'size': 30}),
                'unglued': forms.CheckboxInput(),
            }

class EbookForm(forms.ModelForm):
    class Meta:
        model = Ebook
        exclude =( 'created',)
        widgets = { 
                'edition': forms.HiddenInput, 
                'user': forms.HiddenInput, 
                'provider': forms.HiddenInput, 
                'url': forms.TextInput(attrs={'size' : 60}),
            }
    def clean_provider(self):
        new_provider= Ebook.infer_provider(self.data[self.prefix + '-url'])
        if not new_provider:
            raise forms.ValidationError(_("At this time, ebook URLs must point at Internet Archive, Wikisources, Hathitrust, Project Gutenberg, or Google Books."))
        return new_provider
        
    def clean_url(self):
        url = self.data[self.prefix + '-url']
        try:
            Ebook.objects.get(url=url)
        except Ebook.DoesNotExist:
            return url
        raise forms.ValidationError(_("There's already an ebook with that url."))
        
def UserClaimForm ( user_instance, *args, **kwargs ):
    class ClaimForm(forms.ModelForm):
        i_agree=forms.BooleanField(error_messages={'required': 'You must agree to the Terms in order to claim a work.'})
        rights_holder=forms.ModelChoiceField(queryset=user_instance.rights_holder.all(), empty_label=None)
        
        class Meta:
            model = Claim
            exclude = 'status'
            widgets = { 
                    'user': forms.HiddenInput, 
                    'work': forms.HiddenInput, 
                }

        def __init__(self):
            super(ClaimForm, self).__init__(*args, **kwargs)

    return ClaimForm()
            
class RightsHolderForm(forms.ModelForm):
    owner = AutoCompleteSelectField(
            OwnerLookup,
            label='Owner',
            widget=AutoCompleteSelectWidget(OwnerLookup),
            required=True,
            error_messages={'required': 'Please ensure the owner is a valid Unglue.it account.'},
        )
    email = forms.EmailField(
        label=_("notification email address for rights holder"), 
        max_length=100,
        error_messages={'required': 'Please enter an email address for the rights holder.'},
        )
    class Meta:
        model = RightsHolder

    def clean_rights_holder_name(self):
        rights_holder_name = self.data["rights_holder_name"]
        try:
            RightsHolder.objects.get(rights_holder_name__iexact=rights_holder_name)
        except RightsHolder.DoesNotExist:
            return rights_holder_name
        raise forms.ValidationError(_("Another rights holder with that name already exists."))

    
class ProfileForm(forms.ModelForm):
    clear_facebook=forms.BooleanField(required=False)
    clear_twitter=forms.BooleanField(required=False)
    clear_goodreads=forms.BooleanField(required=False)
    
    class Meta:
        model = UserProfile
        fields = 'tagline', 'librarything_id', 'home_url', 'clear_facebook', 'clear_twitter', 'clear_goodreads', 'avatar_source'
        widgets = {
            'tagline': forms.Textarea(attrs={'rows': 5, 'onKeyUp': "counter(this, 140)", 'onBlur': "counter(this, 140)"}),
        }

    def __init__(self, *args, **kwargs):
        profile = kwargs.get('instance')
        super(ProfileForm, self).__init__(*args, **kwargs)
        choices = []
        for choice in self.fields['avatar_source'].choices :
            if choice[0] == FACEBOOK and not profile.facebook_id:
                pass
            elif choice[0] == TWITTER and not profile.twitter_id:
                pass
            else:
                choices.append(choice)
        self.fields['avatar_source'].choices = choices

    def clean(self):
        # check that if a social net is cleared, we're not using it a avatar source
        if self.cleaned_data.get("clear_facebook", False) and self.cleaned_data.get("avatar_source", None)==FACEBOOK:
            self.cleaned_data["avatar_source"]==GRAVATAR
        if self.cleaned_data.get("clear_twitter", False) and self.cleaned_data.get("avatar_source", None)==TWITTER:
            self.cleaned_data["avatar_source"]==GRAVATAR
        return self.cleaned_data
 
class UserData(forms.Form):
    username = forms.RegexField(
        label=_("New Username"), 
        max_length=30, 
        regex=r'^[\w.@+-]+$',
        help_text = _("30 characters or fewer."),
        error_messages = {
            'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")
        }
    )
    oldusername = None


    def clean_username(self):
        username = self.data["username"]
        if username != self.oldusername:
            users = User.objects.filter(username__iexact=username)
            for user in users:
                raise forms.ValidationError(_("Another user with that username already exists."))
            return username
        raise forms.ValidationError(_("Your username is already "+username))

class CloneCampaignForm(forms.Form):
    campaign_id = forms.IntegerField(required = True, widget = forms.HiddenInput)

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
        fields = 'name', 'work',  'managers'
        widgets = { 'work': forms.HiddenInput }

def getTransferCreditForm(maximum, data=None, *args, **kwargs ):
    class TransferCreditForm(forms.Form):
        recipient = AutoCompleteSelectField(
                OwnerLookup,
                label='Recipient',
                widget=AutoCompleteSelectWidget(OwnerLookup),
                required=True,
                error_messages={'required': 'Please ensure the recipient is a valid Unglue.it account.'},
            )
        amount = forms.IntegerField(
                required=True,
                min_value=1, 
                max_value=maximum,
                label="Transfer Amount",
                error_messages={'min_value': 'Transfer amount must be positive', 'max_value': 'You only have %(limit_value)s available for transfer'},
            )
    return TransferCreditForm( data=data )


class WorkForm(forms.Form):
    other_work = forms.ModelChoiceField(queryset=Work.objects.all(), 
            widget=forms.HiddenInput(), 
            required=True, 
            error_messages={'required': 'Missing work to merge with.'},
            )
    work=None

    def clean_other_work(self):
        if self.cleaned_data["other_work"].id== self.work.id:
            raise forms.ValidationError(_("You can't merge a work into itself"))
        return self.cleaned_data["other_work"]

    def __init__(self, work=None, *args, **kwargs):
        super(WorkForm, self).__init__(*args, **kwargs)
        self.work=work

class OtherWorkForm(WorkForm):
    other_work = AutoCompleteSelectField(
            WorkLookup,
            label='Other Work (title)',
            widget=AutoCompleteSelectWidget(WorkLookup),
            required=True,
            error_messages={'required': 'Missing work to merge with.'},
        )    

    def __init__(self,  *args, **kwargs):
        super(OtherWorkForm, self).__init__(*args, **kwargs)
        self.fields['other_work'].widget.update_query_parameters({'language':self.work.language})
    
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

class CustomPremiumForm(forms.ModelForm):

    class Meta:
        model = Premium
        fields = 'campaign', 'amount', 'description', 'type', 'limit'
        widgets = { 
                'description': forms.Textarea(attrs={'cols': 80, 'rows': 4}),
                'campaign': forms.HiddenInput,
                'type': forms.HiddenInput(attrs={'value':'XX'}),
                'limit': forms.TextInput(attrs={'value':'0'}),
            }
def getManageCampaignForm ( instance, data=None, *args, **kwargs ):
    def get_queryset():
        work=instance.work
        return Edition.objects.filter(work = work)
            
    class ManageCampaignForm(forms.ModelForm):
        paypal_receiver = forms.EmailField(
            label=_("contact email address for this campaign"), 
            max_length=100, 
            error_messages={'required': 'You must enter the email we should contact you at for this campaign.'},
            )
        target = forms.DecimalField( min_value= D(settings.UNGLUEIT_MINIMUM_TARGET), error_messages={'required': 'Please specify a target price.'} )
        edition =  forms.ModelChoiceField(get_queryset(), widget=RadioSelect(),empty_label='no edition selected',required = False,)
        minimum_target = settings.UNGLUEIT_MINIMUM_TARGET
        latest_ending = (timedelta(days=int(settings.UNGLUEIT_LONGEST_DEADLINE)) + now()).date
        publisher = forms.ModelChoiceField(instance.work.publishers(), empty_label='no publisher selected', required = False,)
                
        class Meta:
            model = Campaign
            fields = 'description', 'details', 'license', 'target', 'deadline', 'paypal_receiver', 'edition', 'email', 'publisher'
            widgets = { 
                    'deadline': SelectDateWidget,
                }
    
        def clean_target(self):
            new_target = self.cleaned_data['target']
            if self.instance:
                if self.instance.status == 'ACTIVE' and self.instance.target < new_target:
                    raise forms.ValidationError(_('The fundraising target for an ACTIVE campaign cannot be increased.'))
            if new_target < D(settings.UNGLUEIT_MINIMUM_TARGET):
                raise forms.ValidationError(_('A campaign may not be launched with a target less than $%s' % settings.UNGLUEIT_MINIMUM_TARGET))
            return new_target
        
        def clean_deadline(self):
            new_deadline_date = self.cleaned_data['deadline']
            new_deadline= new_deadline_date + timedelta(hours=23,minutes=59)
            if self.instance:
                if self.instance.status == 'ACTIVE' and self.instance.deadline.date() != new_deadline.date():
                    raise forms.ValidationError(_('The closing date for an ACTIVE campaign cannot be changed.'))
            if new_deadline_date - now() > timedelta(days=int(settings.UNGLUEIT_LONGEST_DEADLINE)):
                raise forms.ValidationError(_('The chosen closing date is more than %s days from now' % settings.UNGLUEIT_LONGEST_DEADLINE))
            elif new_deadline - now() < timedelta(days=0):         
                raise forms.ValidationError(_('The chosen closing date is in the past'))
            return new_deadline
            
        def clean_license(self):
            new_license = self.cleaned_data['license']
            if self.instance:
                if self.instance.status == 'ACTIVE' and self.instance.license != new_license:
                    # should only allow change to a less restrictive license
                    if self.instance.license == 'CC BY-ND' and new_license in ['CC BY-NC-ND','CC BY-NC-SA','CC BY-NC']:
                        raise forms.ValidationError(_('The proposed license for an ACTIVE campaign may not add restrictions.'))
                    elif self.instance.license == 'CC BY' and new_license != 'CC0':
                        raise forms.ValidationError(_('The proposed license for an ACTIVE campaign may not add restrictions.'))
                    elif self.instance.license == 'CC BY-NC' and new_license in ['CC BY-NC-ND','CC BY-NC-SA','CC BY-SA','CC BY-ND']:
                        raise forms.ValidationError(_('The proposed license for an ACTIVE campaign may not add restrictions.'))
                    elif self.instance.license == 'CC BY-ND' and new_license in ['CC BY-NC-ND','CC BY-NC-SA','CC BY-SA','CC BY-NC']:
                        raise forms.ValidationError(_('The proposed license for an ACTIVE campaign may not add restrictions.'))
                    elif self.instance.license == 'CC BY-SA' and new_license in ['CC BY-NC-ND','CC BY-NC-SA','CC BY-ND','CC BY-NC']:
                        raise forms.ValidationError(_('The proposed license for an ACTIVE campaign may not add restrictions.'))
                    elif self.instance.license == 'CC BY-NC-SA' and new_license in ['CC BY-NC-ND','CC BY-ND']:
                        raise forms.ValidationError(_('The proposed license for an ACTIVE campaign may not add restrictions.'))
                    elif self.instance.license == 'CC0' :
                        raise forms.ValidationError(_('The proposed license for an ACTIVE campaign may not add restrictions.'))
            return new_license
    return ManageCampaignForm(instance = instance, data=data)

class CampaignPledgeForm(forms.Form):
    preapproval_amount = forms.DecimalField(
        required = False,
        min_value=D('1.00'),
        max_value=D('2000.00'), 
        decimal_places=2, 
        label="Pledge Amount",
    )
    anonymous = forms.BooleanField(required=False, label=_("Make this pledge anonymous, please"))
    ack_name = forms.CharField(required=False, max_length=64, label=_("What name should we display?"))
    ack_dedication = forms.CharField(required=False, max_length=140, label=_("Your dedication:"))

    premium_id = forms.IntegerField(required=False)
    premium=None
    
    @property
    def pledge_extra(self):
        return PledgeExtra( anonymous=self.cleaned_data['anonymous'],
                            ack_name=self.cleaned_data['ack_name'],
                            ack_dedication=self.cleaned_data['ack_dedication'],
                            premium=self.premium)
        
    def clean_preapproval_amount(self):
        preapproval_amount = self.cleaned_data['preapproval_amount']
        if preapproval_amount is None:
            raise forms.ValidationError(_("Please enter a pledge amount."))
        return preapproval_amount
    
    def clean_premium_id(self):
        premium_id = self.cleaned_data['premium_id']
        try:
            self.premium= Premium.objects.get(id=premium_id)
            if self.premium.limit>0:
                if self.premium.limit<=self.premium.premium_count:
                    raise forms.ValidationError(_("Sorry, that premium is fully subscribed."))
        except  Premium.DoesNotExist:
            raise forms.ValidationError(_("Sorry, that premium is not valid."))
        
    def clean(self):
        # check on whether the preapproval amount is < amount for premium tier. If so, put an error message
        preapproval_amount = self.cleaned_data.get("preapproval_amount")
        if preapproval_amount is None:
            # preapproval_amount failed validation, that error is the relevant one
            return self.cleaned_data
        elif self.premium is None:
            raise forms.ValidationError(_("Please select a premium." ))            
        elif preapproval_amount < self.premium.amount:
            logger.info("raising form validating error")
            raise forms.ValidationError(_("Sorry, you must pledge at least $%s to select that premium." % (self.premium.amount)))
        return self.cleaned_data

class PlainCCForm(forms.Form):
    stripe_token = forms.CharField(required=False, widget=forms.HiddenInput())

class CCForm(PlainCCForm):
    username = forms.CharField(max_length=30, required=True, widget=forms.HiddenInput())
    work_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    preapproval_amount= forms.DecimalField(
        required=False,
        min_value=D('1.00'), 
        max_value=D('100000.00'), 
        decimal_places=2, 
        label="Pledge",
    )

class DonateForm(forms.Form):
    preapproval_amount = forms.DecimalField( widget=forms.HiddenInput() )
    username = forms.CharField(max_length=30, required=True, widget=forms.HiddenInput() )
    work_id = forms.IntegerField(required=False,  widget=forms.HiddenInput() )
    title = forms.CharField(max_length=200, required=False, widget=forms.HiddenInput() )
    
    
class GoodreadsShelfLoadingForm(forms.Form):
    goodreads_shelf_name_number = forms.CharField(widget=forms.Select(choices=(
                ('all','all'),
                )))

class LibraryThingForm(forms.Form):
    lt_username = forms.CharField(max_length=30, required=True)

class PledgeCancelForm(forms.Form):
    # which campaign whose active transaction to cancel?
    campaign_id = forms.IntegerField(required=True, widget=forms.HiddenInput())


class CampaignAdminForm(forms.Form):
    campaign_id = forms.IntegerField()
    
class EmailShareForm(forms.Form):
    recipient = forms.EmailField(error_messages={'required': 'Please specify a recipient.'})
    subject = forms.CharField(max_length=100, error_messages={'required': 'Please specify a subject.'})
    message = forms.CharField(widget=forms.Textarea(), error_messages={'required': 'Please include a message.'})
    # allows us to return user to original page by passing it as hidden form input
    # we can't rely on POST or GET since the emailshare view handles both
    # and may iterate several times as it catches user errors, losing URL info
    next = forms.CharField(widget=forms.HiddenInput())
    
class FeedbackForm(forms.Form):
    sender = forms.EmailField(widget=forms.TextInput(attrs={'size':50}), label="Your email", error_messages={'required': 'Please specify your email address.'})
    subject = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'size':50}), error_messages={'required': 'Please specify a subject.'})
    message = forms.CharField(widget=forms.Textarea(), error_messages={'required': 'Please specify a message.'})
    page = forms.CharField(widget=forms.HiddenInput())
    notarobot = forms.IntegerField(label="Please prove you're not a robot", error_messages={'required': "You must do the sum to prove you're not a robot."})
    answer = forms.IntegerField(widget=forms.HiddenInput())
    num1 = forms.IntegerField(widget=forms.HiddenInput())
    num2 = forms.IntegerField(widget=forms.HiddenInput())
    
    def clean(self):
        cleaned_data = self.cleaned_data
        notarobot = str(cleaned_data.get("notarobot"))
        answer = str(cleaned_data.get("answer"))
        if notarobot != answer:
            raise forms.ValidationError(_("Whoops, try that sum again."))
            
        return cleaned_data

class AuthForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        if request and request.method == 'GET':
            saved_un= request.COOKIES.get('un', None)
            super(AuthForm, self).__init__(initial={"username":saved_un},*args, **kwargs)
        else:
            super(AuthForm, self).__init__(*args, **kwargs)

class MsgForm(forms.Form):
    msg = forms.CharField(widget=forms.Textarea(), error_messages={'required': 'Please specify a message.'})

    def full_clean(self):
        super(MsgForm,self).full_clean()
        if self.data.has_key("supporter"):
            try:
                self.cleaned_data['supporter'] = User.objects.get(id=self.data["supporter"])
            except User.DoesNotExist:
                raise ValidationError("Supporter does not exist")
        else:
            raise ValidationError("Supporter is not specified")
        if self.data.has_key("work"):
            try:
                self.cleaned_data['work'] = Work.objects.get(id=self.data["work"])
            except Work.DoesNotExist:
                raise ValidationError("Work does not exist")
        else:
            raise ValidationError("Work is not specified")
            
class PressForm(forms.ModelForm):
    class Meta:
        model = Press

        widgets = { 
                'date': SelectDateWidget(years=range(2010,2025)),
            }

