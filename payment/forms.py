from django import forms
import logging

logger = logging.getLogger(__name__)

class StripePledgeForm(forms.Form):
    stripeToken = forms.CharField(required=False, widget=forms.HiddenInput())
    
class BalancedPledgeForm(forms.Form):
    card_uri = forms.CharField(required=False, widget=forms.HiddenInput())
    
class WepayPledgeForm(forms.Form):
    pass