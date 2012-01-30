import datetime
from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import validate_email
from django.utils.translation import ugettext_lazy as _
from django.forms.extras.widgets import SelectDateWidget

from decimal import Decimal as D
from selectable.forms import AutoCompleteSelectMultipleWidget,AutoCompleteSelectMultipleField
from selectable.forms import AutoCompleteSelectWidget,AutoCompleteSelectField

from regluit.core.models import UserProfile, RightsHolder, Claim, Campaign, Premium
from regluit.core.lookups import OwnerLookup

import logging

logger = logging.getLogger(__name__)


def UserClaimForm ( user_instance, *args, **kwargs ):
    class ClaimForm(forms.ModelForm):
        i_agree=forms.BooleanField()
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
        )
    email = forms.EmailField(
        label=_("notification email address for rights holder"), 
        max_length=100, 
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
            'tagline': forms.Textarea(attrs={'cols': 25, 'rows': 5}),
        }

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
            required=False,
        )
    userid = forms.IntegerField( required = True, widget = forms.HiddenInput )
    class Meta:
        model = Campaign
        fields = 'name', 'work',  'managers'
        widgets = { 'work': forms.HiddenInput }

class ManageCampaignForm(forms.ModelForm):
    paypal_receiver = forms.EmailField(
        label=_("email address to collect Paypal funds"), 
        max_length=100, 
        )
    target = forms.DecimalField( min_value= D('0.00') )
    class Meta:
        model = Campaign
        fields = 'description', 'details', 'target', 'deadline', 'paypal_receiver'
        widgets = { 
                'description': forms.Textarea(attrs={'cols': 80, 'rows': 20}),
                'details': forms.Textarea(attrs={'cols': 80, 'rows': 20}),
                'deadline': SelectDateWidget
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
        if new_deadline-datetime.datetime.today() > datetime.timedelta(days=int(settings.UNGLUEIT_LONGEST_DEADLINE)):
            raise forms.ValidationError(_('The chosen closing date is more than %s days from now' % settings.UNGLUEIT_LONGEST_DEADLINE))
        elif new_deadline-datetime.datetime.today() < datetime.timedelta(days=int(settings.UNGLUEIT_SHORTEST_DEADLINE)):         
            raise forms.ValidationError(_('The chosen closing date is less than %s days from now' % settings.UNGLUEIT_SHORTEST_DEADLINE))
        return new_deadline

class CampaignPledgeForm(forms.Form):
    preapproval_amount = forms.DecimalField(
        required=False,
        min_value=D('1.00'), 
        max_value=D('10000.00'), 
        decimal_places=2, 
        label="Pledge Amount",
    )
    anonymous = forms.BooleanField(required=False, label=_("Don't display my username in the supporters list"))

    premium_id = forms.IntegerField(required=False)
        
    def clean(self):
        cleaned_data = self.cleaned_data
        # check on whether the preapproval amount is < amount for premium tier. If so, put an error message
        try:
            preapproval_amount = cleaned_data.get("preapproval_amount")
            premium_id =  int(cleaned_data.get("premium_id"))
            premium_amount = Premium.objects.get(id=premium_id).amount
            if preapproval_amount < premium_amount:
                raise forms.ValidationError(_("Sorry, you must pledge at least $%s to select that premium." % (premium_amount)))
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
	recipient = forms.EmailField()
	sender = forms.EmailField(widget=forms.HiddenInput())
	subject = forms.CharField(max_length=100)
	message = forms.CharField(widget=forms.Textarea())
	# allows us to return user to original page by passing it as hidden form input
	# we can't rely on POST or GET since the emailshare view handles both
	# and may iterate several times as it catches user errors, losing URL info
	next = forms.CharField(widget=forms.HiddenInput())
	
class FeedbackForm(forms.Form):
	sender = forms.EmailField(widget=forms.TextInput(attrs={'size':50}), label="Your email")
	subject = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'size':50}))
	message = forms.CharField(widget=forms.Textarea())
	page = forms.CharField(widget=forms.HiddenInput())
	notarobot = forms.IntegerField(label="Please prove you're not a robot")
	answer = forms.IntegerField(widget=forms.HiddenInput())
	num1 = forms.IntegerField(widget=forms.HiddenInput())
	num2 = forms.IntegerField(widget=forms.HiddenInput())
	
	def clean(self):
		cleaned_data = self.cleaned_data
		notarobot = str(cleaned_data.get("notarobot"))
		answer = str(cleaned_data.get("answer"))
		if notarobot!=answer:
			raise forms.ValidationError(_("Whoops, try that sum again."))
			
		return cleaned_data
