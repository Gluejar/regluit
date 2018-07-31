import logging
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from registration.forms import RegistrationFormUniqueEmail
from .emailcheck import is_disposable
from .models import Library

logger = logging.getLogger(__name__)

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
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two passwords don't match."))
        return password2

class RegistrationFormNoDisposableEmail(RegistrationFormUniqueEmail):
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
