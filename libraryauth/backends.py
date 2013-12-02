'''
to make a backend named <backend> you need to...
1. make a class <backend>
2. with a function authenticate(self, request, library)
    returns true if can request.user can be authenticated to the library, and attaches a credential property to the library object
    returns fals if otherwise.
3. with a class authenticator
    with a process((self, authenticator, success_url, deny_url) method which is expected to return a response
4. make a libraryauth/<backend>_join.html template (authenticator will be in its context) to insert a link or form for a user to join the library
5. if you need to show the user a form, define a model form class form with init method  __init__(self, request, library, *args, **kwargs)
    and model LibraryUser
6. define an admin form to let the library configure its authentication
7. add new auth choice to Library.backend choices and the admin as desired

'''
import logging
from django.db.models import Q
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .models import Block, IP, LibraryUser, CardPattern, EmailPattern
                    

logger = logging.getLogger(__name__)

class ip:
    def authenticate(self,request, library):
        try:
            ip = IP(request.META['REMOTE_ADDR'])
            blocks = Block.objects.filter(Q(lower=ip) | Q(lower__lte=ip, upper__gte=ip))
            for block in blocks:
                if block.library==library:
                    logger.info('%s authenticated for %s from %s'%(request.user, library, ip))
                    library.credential=ip
                    return True
            return False
        except KeyError:
            return False
     
    class authenticator():
        def process(authenticator, success_url, deny_url):
            return HttpResponseRedirect(deny_url)
    
    form = None
    
    class admin_form(forms.ModelForm):
        class Meta:
            model = Block
            exclude = "library"

class cardnum:   
    def authenticate(self,request, library):
        return False

    class authenticator():
        def process(self, authenticator, success_url, deny_url):
            if authenticator.form and authenticator.request.method=='POST' and authenticator.form.is_valid():
                library = authenticator.form.cleaned_data['library']
                library.credential = authenticator.form.cleaned_data['credential']
                logger.info('%s authenticated for %s from %s'%(authenticator.request.user, authenticator.library, authenticator.form.cleaned_data.get('number')))
                library.add_user(authenticator.form.cleaned_data['user'])
                return HttpResponseRedirect(success_url)
            else:
                return render(authenticator.request, 'libraryauth/library.html', {
                        'library':authenticator.library,
                        'authenticator':authenticator,
                        })

    class admin_form(forms.ModelForm):
        class Meta:
            model = CardPattern
            exclude = "library"
    
    class form(forms.ModelForm):
        credential = forms.RegexField(
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
                super(cardnum.form, self).__init__(data=data)
            else:
                initial={'user':request.user, 'library':library}
                super(cardnum.form, self).__init__(initial=initial)
    
        def clean(self):
            library = self.cleaned_data.get('library', None)
            credential = self.cleaned_data.get('credential', '')
            for card_pattern in library.cardnum_auths.all():
                if card_pattern.is_valid(credential):
                    return self.cleaned_data
            raise forms.ValidationError("the library card number must be VALID.")
        
        class Meta:
            model = LibraryUser
            widgets = { 'library': forms.HiddenInput, 'user': forms.HiddenInput }
class email:  
    def authenticate(self,request, library):
        if request.user.is_anonymous():
            return False
        email = request.user.email
        for email_pattern in library.email_auths.all():
            if email_pattern.is_valid(email):
                logger.info('%s authenticated for %s from %s'%(request.user, library, email))
                library.credential=email
                return True
        return False
     
    class authenticator():
        def process(authenticator, success_url, deny_url):
            return HttpResponseRedirect(deny_url)
    form = None
    class admin_form(forms.ModelForm):
        class Meta:
            model = EmailPattern
            exclude = "library"
