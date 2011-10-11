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
            'tagline': forms.Textarea(attrs={'cols': 70, 'rows': 2}),
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
   # oldusername = forms.CharField(max_length=30)


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
    pledge_amount = forms.DecimalField(min_value=D('0.00'), max_value=D('10000.00'), decimal_places=2)
