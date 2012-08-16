from django import forms
import logging

logger = logging.getLogger(__name__)

class StripePledgeForm(forms.Form):
    stripeToken = forms.CharField(required=False, widget=forms.HiddenInput())