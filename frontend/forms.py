from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from decimal import Decimal as D
from selectable.forms import AutoCompleteSelectWidget,AutoCompleteSelectField
from selectable.forms import AutoCompleteSelectMultipleWidget,AutoCompleteSelectMultipleField

from regluit.core.models import UserProfile, RightsHolder, Claim, Campaign
from regluit.core.lookups import OwnerLookup

class ClaimForm(forms.ModelForm):
    i_agree=forms.BooleanField()
    class Meta:
        model = Claim
        exclude = 'status'
        widgets = { 'user': forms.HiddenInput, 'work': forms.HiddenInput }

class RightsHolderForm(forms.ModelForm):
    owner = AutoCompleteSelectField(
            OwnerLookup,
            label='Owner',
            widget=AutoCompleteSelectWidget(OwnerLookup),
            required=True,
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

class AutoCompleteSelectManyToManyField(AutoCompleteSelectField):
	def to_python(self, value):
		single_value = AutoCompleteSelectField.to_python(self, value)
		return [single_value,]

class OpenCampaignForm(forms.ModelForm):
    manager = AutoCompleteSelectMultipleField(
            OwnerLookup,
            label='Campaign Manager',
            widget=AutoCompleteSelectMultipleWidget(OwnerLookup),
            required=False,
        )
    userid = forms.IntegerField( required = True, widget = forms.HiddenInput )
    class Meta:
        model = Campaign
        fields = 'name', 'work', 'target', 'deadline', 'manager'
        widgets = { 'work': forms.HiddenInput }

    #def clean_manager(self):
    	#value = self.data["manager"]
        #value= self.manager.clean()
        #if value:
        	#return value
        #return self.userid.clean()

class CampaignPledgeForm(forms.Form):
    preapproval_amount = forms.DecimalField(
        initial=None, 
        required=True, 
        min_value=D('0.00'), 
        max_value=D('10000.00'), 
        decimal_places=2, 
        label="Pledge Amount",
    )
    anonymous = forms.BooleanField(required=False, label="Don't display my username in the supporters list")
    
class GoodreadsShelfLoadingForm(forms.Form):
    goodreads_shelf_name_number = forms.CharField(widget=forms.Select(choices=(
                ('all','all'),
                )))

class LibraryThingForm(forms.Form):
    lt_username = forms.CharField(max_length=30, required=True)
