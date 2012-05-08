from datetime import timedelta
from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import validate_email
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import RadioSelect
from django.forms.extras.widgets import SelectDateWidget

from decimal import Decimal as D
from selectable.forms import AutoCompleteSelectMultipleWidget,AutoCompleteSelectMultipleField
from selectable.forms import AutoCompleteSelectWidget,AutoCompleteSelectField

from regluit.core.models import UserProfile, RightsHolder, Claim, Campaign, Premium, Ebook, Edition
from regluit.core.lookups import OwnerLookup

from regluit.utils.localdatetime import now

import logging

logger = logging.getLogger(__name__)

class EbookForm(forms.ModelForm):
    class Meta:
        model = Ebook
        exclude = 'created'
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
        fields = 'tagline', 'librarything_id', 'home_url', 'clear_facebook', 'clear_twitter', 'clear_goodreads'
        widgets = {
            'tagline': forms.Textarea(attrs={'rows': 5, 'onKeyUp': "counter(this, 140)", 'onBlur': "counter(this, 140)"}),
        }

class UserEmail(forms.Form):
    email = forms.EmailField(
        label=_("new email address"), 
        max_length=100,
        error_messages={'required': 'Please enter an email address.'},
        )
    
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


    def clean_username(self):
        username = self.data["username"]
        oldusername = self.data["oldusername"]
        if username != oldusername:
            try:
                User.objects.get(username__iexact=username)
            except User.DoesNotExist:
                return username
            raise forms.ValidationError(_("Another user with that username already exists."))
        raise forms.ValidationError(_("Your username is already "+oldusername))

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
                'description': forms.Textarea(attrs={'cols': 80, 'rows': 2}),
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
            label=_("email address to collect Paypal funds"), 
            max_length=100, 
            error_messages={'required': 'You must enter the email associated with your Paypal account.'},
            required = False,
            )
        target = forms.DecimalField( min_value= D(settings.UNGLUEIT_MINIMUM_TARGET), error_messages={'required': 'Please specify a target price.'} )
        edition =  forms.ModelChoiceField(get_queryset(), widget=RadioSelect(),empty_label='no edition selected')
        minimum_target = settings.UNGLUEIT_MINIMUM_TARGET
        latest_ending = (timedelta(days=int(settings.UNGLUEIT_LONGEST_DEADLINE)) + now()).date
                
        class Meta:
            model = Campaign
            fields = 'description', 'details', 'license', 'target', 'deadline', 'paypal_receiver', 'edition'
            widgets = { 
                    'description': forms.Textarea(attrs={'cols': 80, 'rows': 20}),
                    'details': forms.Textarea(attrs={'cols': 80, 'rows': 5}),
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
            new_deadline = self.cleaned_data['deadline']
            if self.instance:
                if self.instance.status == 'ACTIVE' and self.instance.deadline != new_deadline:
                    raise forms.ValidationError(_('The closing date for an ACTIVE campaign cannot be changed.'))
            if new_deadline - now() > timedelta(days=int(settings.UNGLUEIT_LONGEST_DEADLINE)):
                raise forms.ValidationError(_('The chosen closing date is more than %s days from now' % settings.UNGLUEIT_LONGEST_DEADLINE))
            elif new_deadline - now() < timedelta(days=int(settings.UNGLUEIT_SHORTEST_DEADLINE)):         
                raise forms.ValidationError(_('The chosen closing date is less than %s days from now' % settings.UNGLUEIT_SHORTEST_DEADLINE))
            return new_deadline
            
        def clean_license(self):
            new_license = self.cleaned_data['license']
            if self.instance:
                if self.instance.status == 'ACTIVE' and self.instance.license != new_license:
                    raise forms.ValidationError(_('The license for an ACTIVE campaign cannot be changed.'))
            return new_license
    return ManageCampaignForm(instance = instance, data=data)

class CampaignPledgeForm(forms.Form):
    preapproval_amount = forms.DecimalField(
        required = False,
        min_value=D('1.00'),
        max_value=D('10000.00'), 
        decimal_places=2, 
        label="Pledge Amount",
    )
    anonymous = forms.BooleanField(required=False, label=_("Don't display my username in the supporters list"))

    premium_id = forms.IntegerField(required=False)
    
    def clean_preapproval_amount(self):
        data = self.cleaned_data['preapproval_amount']
        if data is None:
            raise forms.ValidationError(_("Please enter a pledge amount."))
        return data
    
    # should we do validation on the premium_id here?
    # can see whether it corresponds to a real premium -- do that here?
    # can also figure out moreover whether it's one of the allowed premiums for that campaign....
        
    def clean(self):
        cleaned_data = self.cleaned_data
        # check on whether the preapproval amount is < amount for premium tier. If so, put an error message
        try:
            preapproval_amount = cleaned_data.get("preapproval_amount")
            premium_id =  int(cleaned_data.get("premium_id"))
            premium_amount = Premium.objects.get(id=premium_id).amount
            logger.info("preapproval_amount: {0}, premium_id: {1}, premium_amount:{2}".format(preapproval_amount, premium_id, premium_amount))
            if preapproval_amount < premium_amount:
                logger.info("raising form validating error")
                raise forms.ValidationError(_("Sorry, you must pledge at least $%s to select that premium." % (premium_amount)))
            try:
                premium= Premium.objects.get(id=premium_id)
                if premium.limit>0:
                    if premium.limit<=premium.premium_count:
                        raise forms.ValidationError(_("Sorry, that premium is fully subscribed."))
            except  Premium.DoesNotExist:
                raise forms.ValidationError(_("Sorry, that premium is not valid."))

        except Exception, e:
            if isinstance(e, forms.ValidationError):
                raise e
            
        return cleaned_data

class DonateForm(forms.Form):
    donation_amount = forms.DecimalField(
        required=False,
        min_value=D('1.00'), 
        max_value=D('100000.00'), 
        decimal_places=2, 
        label="Donation",
    )
    anonymous = forms.BooleanField(required=False, label=_("Don't display my username in the donors' list"))
        
    def clean(self):
        cleaned_data = self.cleaned_data         
        return cleaned_data

class GoodreadsShelfLoadingForm(forms.Form):
    goodreads_shelf_name_number = forms.CharField(widget=forms.Select(choices=(
                ('all','all'),
                )))

class LibraryThingForm(forms.Form):
    lt_username = forms.CharField(max_length=30, required=True)
    
class CampaignAdminForm(forms.Form):
    pass
    
class EmailShareForm(forms.Form):
    recipient = forms.EmailField(error_messages={'required': 'Please specify a recipient.'})
    sender = forms.EmailField(widget=forms.HiddenInput())
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
