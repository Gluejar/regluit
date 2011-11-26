from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.forms.extras.widgets import SelectDateWidget

from decimal import Decimal as D
from selectable.forms import AutoCompleteSelectMultipleWidget,AutoCompleteSelectMultipleField
from selectable.forms import AutoCompleteSelectWidget,AutoCompleteSelectField

from regluit.core.models import UserProfile, RightsHolder, Claim, Campaign
from regluit.core.lookups import OwnerLookup

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
    class Meta:
        model = UserProfile
        fields = 'tagline', 'librarything_id', 'home_url', 'clear_facebook', 'clear_twitter'
        widgets = {
            'tagline': forms.Textarea(attrs={'cols': 35, 'rows': 4}),
        }

class UserData(forms.Form):
    username = forms.RegexField(
        label=_("New Username"), 
        max_length=30, 
        regex=r'^[\w.@+-]+$',
        help_text = _("30 characters or less."),
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
        fields = 'name', 'work', 'target', 'deadline', 'managers'
        widgets = { 'work': forms.HiddenInput, 'deadline': SelectDateWidget }

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
        return new_target

    def clean_deadline(self):
        new_deadline = self.cleaned_data['deadline']
        if self.instance:
            if self.instance.status == 'ACTIVE' and self.instance.deadline != new_deadline:
                raise forms.ValidationError(_('The closing date for an ACTIVE campaign cannot be changed.'))
        return new_deadline

class CampaignPledgeForm(forms.Form):
    preapproval_amount = forms.DecimalField(
        initial=None, 
        required=True, 
        min_value=D('0.00'), 
        max_value=D('10000.00'), 
        decimal_places=2, 
        label="Pledge Amount",
    )
    anonymous = forms.BooleanField(required=False, label=_("Don't display my username in the supporters list"))
    
class GoodreadsShelfLoadingForm(forms.Form):
    goodreads_shelf_name_number = forms.CharField(widget=forms.Select(choices=(
                ('all','all'),
                )))

class LibraryThingForm(forms.Form):
    lt_username = forms.CharField(max_length=30, required=True)
