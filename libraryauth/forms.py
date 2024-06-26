import logging
from random import randint

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _


# hack to fix bug in old version of django-registration
from registration.validators import CONFUSABLE_EMAIL
from confusable_homoglyphs import confusables
def validate_confusables_email(value):
    if '@' not in value:
        return
    parts = value.split('@')
    if len(parts) != 2:
        raise forms.ValidationError(CONFUSABLE_EMAIL, code='invalid')
    local_part, domain = value.split('@')
    if confusables.is_dangerous(local_part) or \
       confusables.is_dangerous(domain):
        raise forms.ValidationError(CONFUSABLE_EMAIL, code='invalid')

import registration
registration.validators.validate_confusables_email = validate_confusables_email
# end hack

from registration.forms import RegistrationFormUniqueEmail
from .emailcheck import is_disposable
from .models import Library

logger = logging.getLogger(__name__)

rands = [randint(0,99) for i in range(0, 21)]
encoder = {k:v for (k,v) in zip(range(0, 21), rands)}
decoder = {v:k for (k,v) in zip(range(0, 21), rands)}

encode_answers = cache.get('encode_answers')
decode_answers = cache.get('decode_answers')
if not encode_answers:
    cache.set('encode_answers', encoder, None)
if not decode_answers:
    cache.set('decode_answers', decoder, None)
    decode_answers = decoder


class UserData(forms.Form):
    username = forms.RegexField(
        label=_("New Username"),
        max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text=_("30 characters or fewer."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")
        }
    )
    oldusername = None
    allow_same = False


    def clean_username(self):
        username = self.data["username"]
        if username != self.oldusername:
            users = User.objects.filter(username__iexact=username)
            for user in users:
                raise forms.ValidationError(_("Another user with that username already exists."))
            return username
        if not self.allow_same:
            raise forms.ValidationError(_("Your username is already "+username))

class UserNamePass(UserData):
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification.")
    )
    allow_same = True
    notarobot = forms.IntegerField(
        label="Please show you're not a robot.",
        error_messages={
            'required': "",
        },   
        widget=forms.TextInput(attrs={'style': 'width: 2em'}),
    )
    encode_answers = cache.get('encode_answers')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two passwords don't match."))

        return password2

    def clean_notarobot(self):
        notarobot = int(self.data["notarobot"])
        encoded_answer = self.encode_answers.get(notarobot, 'miss')
        tries = self.data.get("tries", -1)
        if str(encoded_answer) != tries:
            raise forms.ValidationError("(Hint: it's addition)")

        return notarobot

class RegistrationFormNoDisposableEmail(RegistrationFormUniqueEmail, UserNamePass):
    def clean_email(self):
        """
        Check the supplied email address against a list of known disposable
        webmail domains.
        """
        cleaned_email = super(RegistrationFormNoDisposableEmail, self).clean_email()
        logger.info('cleaning email')
        if is_disposable(cleaned_email):
            raise forms.ValidationError(_("Please supply a permanent email address."))
        return cleaned_email

class SocialAwarePasswordResetForm(PasswordResetForm):
    def get_users(self, email):
        """
        Send the reset form even if the user password is not usable
        """
        active_users = get_user_model()._default_manager.filter(
            email__iexact=email, is_active=True)
        return active_users

    def clean_email(self):
        email = self.cleaned_data['email']
        if not get_user_model().objects.filter(email__iexact=email, is_active=True).exists():
            raise forms.ValidationError("There aren't ungluers with that email address!")
        return email


class NewLibraryForm(forms.ModelForm):
    username = forms.RegexField(
        label=_("Library Username"),
        max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text=_("30 characters or fewer."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")
        },
        initial='',
    )
    email = forms.EmailField(
        label=_("notification email address for library"),
        max_length=100,
        error_messages={'required': 'Please enter an email address for the library.'},
        )

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.get(username=username)
            raise forms.ValidationError(_(
                "That username is already in use, please choose another."
            ))
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
