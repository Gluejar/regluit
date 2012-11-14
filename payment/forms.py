from django import forms
import logging

logger = logging.getLogger(__name__)

class StripePledgeForm(forms.Form):
    stripeToken = forms.CharField(required=True, widget=forms.HiddenInput())
