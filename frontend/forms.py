from django import forms
from django.db import models
from regluit.core.models import UserProfile
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from decimal import Decimal as D
 
class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = 'user'
        widgets = {
            'tagline': forms.Textarea(attrs={'cols': 35, 'rows': 4}),
            'twitter_id': forms.TextInput(attrs={'label': 'Twitter Handle', 'maxlength': 16}),
        }
        
    def clean_twitter_id(self):
        twitter_id=self.cleaned_data['twitter_id']
        return twitter_id.lstrip('@')

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
                User.objects.get(username=username)
            except User.DoesNotExist:
                return username
            raise forms.ValidationError(_("Another user with that username already exists."))
        raise forms.ValidationError(_("Your username is already "+oldusername))

class CampaignPledgeForm(forms.Form):
    preapproval_amount = forms.DecimalField(initial=None, required=True, min_value=D('0.00'), max_value=D('10000.00'), decimal_places=2, label="Pledge Amount")
    anonymous = forms.BooleanField(required=False, label="Don't display my username in the supporters list")
    
class GoodreadsShelfLoadingForm(forms.Form):
    goodreads_shelf_name = forms.CharField(widget=forms.Select(choices=(
                ('all','all'),
                )))