from django import forms
import logging

logger = logging.getLogger(__name__)

class StripePledgeForm(forms.Form):
    stripe_token = forms.CharField(required=False, widget=forms.HiddenInput())
