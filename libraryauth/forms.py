import logging
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from registration.forms import RegistrationForm
from .emailcheck import is_disposable
from .models import Library

logger = logging.getLogger(__name__)

class RegistrationFormNoDisposableEmail(RegistrationForm):
    def clean_email(self):
        """
        Check the supplied email address against a list of known disposable
        webmail domains.
        """
        logger.info('cleaning email')
        if is_disposable(self.cleaned_data['email']):
            raise forms.ValidationError(_("Please supply a permanent email address."))
        return self.cleaned_data['email']
    

class AuthForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        if request and request.method == 'GET':
            saved_un= request.COOKIES.get('un', None)
            super(AuthForm, self).__init__(initial={"username":saved_un},*args, **kwargs)
        else:
            super(AuthForm, self).__init__(*args, **kwargs)
            
class NewLibraryForm(forms.ModelForm):
    username = forms.RegexField(
        label=_("Library Username"), 
        max_length=30, 
        regex=r'^[\w.@+-]+$',
        help_text = _("30 characters or fewer."),
        error_messages = {
            'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")
        },
        initial = '',
    )
    email = forms.EmailField(
        label=_("notification email address for library"), 
        max_length=100,
        error_messages={'required': 'Please enter an email address for the library.'},
        )
    def clean_username(self):
        username= self.cleaned_data['username']
        try:
            user = User.objects.get(username=username)
            raise forms.ValidationError(_("That username is already in use, please choose another."))
        except User.DoesNotExist:
            self.instance.user = User(username=username)
            return username
            
    
    class Meta:
        model = Library
        fields = 'name', 'backend', 'email', 'username'
        widgets = {'name':forms.TextInput(attrs={'size':'40'})}

class LibraryForm(forms.ModelForm):    
    class Meta:
        model = Library
        fields = 'name', 'backend', 
