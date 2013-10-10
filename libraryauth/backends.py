import logging
from django.db.models import Q
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .models import Block, IP, UserCard

logger = logging.getLogger(__name__)

def ip_authenticate(request, library):
    try:
        ip = IP(request.META['REMOTE_ADDR'])
        print str(ip)
        blocks = Block.objects.filter(Q(lower=ip) | Q(lower__lte=ip, upper__gte=ip))
        for block in blocks:
            if block.library==library:
                logger.info('%s authenticated for %s from %s'%(request.user, library, ip))
                return True
        return False
    except KeyError:
        return False
     
class ip_authenticator():
    def process(authenticator, success_url, deny_url):
        return HttpResponseRedirect(deny_url)
    
def cardnum_authenticate(request, library):
    return False

class cardnum_authenticator():
    def process(self, authenticator, success_url, deny_url):
        if authenticator.form and authenticator.request.method=='POST' and authenticator.form.is_valid():
            authenticator.form.save()
            logger.info('%s authenticated for %s from %s'%(authenticator.request.user, authenticator.library, authenticator.form.cleaned_data.get('number')))
            authenticator.form.cleaned_data['library'].add_user(authenticator.form.cleaned_data['user'])
            return HttpResponseRedirect(success_url)
        else:
            return render(authenticator.request, 'libraryauth/library.html', {
                    'library':authenticator.library,
                    'authenticator':authenticator,
                    })

class cardnum_form(forms.ModelForm):
    number = forms.RegexField(
            label="Enter Your Library Card Number", 
            max_length=20, 
            regex=r'^\d+$',
            required = True,
            help_text = "(digits only)",
            error_messages = {'invalid': "digits only!",}
        )
    def __init__(self, request, library, *args, **kwargs):
        if request.method=="POST":
            data=request.POST
            super(cardnum_form, self).__init__(data=data)
        else:
            initial={'user':request.user, 'library':library}
            super(cardnum_form, self).__init__(initial=initial)
    
    def clean(self):
        library = self.cleaned_data.get('library', None)
        number = self.cleaned_data.get('number', '')
        for card_pattern in library.card_patterns.all():
            if card_pattern.is_valid(number):
                return self.cleaned_data
        raise forms.ValidationError("the library card number must be VALID.")
        
    class Meta:
        model = UserCard
        widgets = { 'library': forms.HiddenInput, 'user': forms.HiddenInput }