import logging

from django import forms

logger = logging.getLogger(__name__)

class StripePledgeForm(forms.Form):
    stripeToken = forms.CharField(required=True, widget=forms.HiddenInput())
