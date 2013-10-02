from . import models

from selectable.forms import AutoCompleteSelectWidget,AutoCompleteSelectField
from selectable.base import ModelLookup
from selectable.registry import registry

from django import forms
from django.contrib.admin import ModelAdmin
from django.contrib.auth.models import User

class UserLookup(ModelLookup):
    model = User
    search_fields = ('username__icontains',)

registry.register(UserLookup)

class LibraryAdminForm(forms.ModelForm):
    user = AutoCompleteSelectField(
            UserLookup,
            widget=AutoCompleteSelectWidget(UserLookup),
            required=True,
        )
    class Meta(object):
        model = models.Library

class LibraryAdmin(ModelAdmin):
    list_display = ('user', )
    form = LibraryAdminForm
    search_fields = ['user__username']


