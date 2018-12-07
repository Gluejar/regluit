from django import forms
from django.contrib.admin import ModelAdmin, site, register
from django.contrib.auth.models import User

from selectable.base import ModelLookup
from selectable.forms import AutoCompleteSelectWidget, AutoCompleteSelectField
from selectable.registry import registry

from . import models

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
    owner = AutoCompleteSelectField(
        UserLookup,
        widget=AutoCompleteSelectWidget(UserLookup),
        required=True,
    )
    class Meta(object):
        model = models.Library
        widgets = {'group':forms.HiddenInput}
        exclude = ('group', )

@register(models.Library)
class LibraryAdmin(ModelAdmin):
    list_display = ('user', )
    form = LibraryAdminForm
    search_fields = ['user__username']

@register(models.Block)
class BlockAdmin(ModelAdmin):
    list_display = ('library', 'lower', 'upper',)
    search_fields = ('library__name', 'lower', 'upper',)

@register(models.CardPattern)
class CardPatternAdmin(ModelAdmin):
    list_display = ('library', 'pattern', 'checksum',)
    search_fields = ('library__name', )

@register(models.EmailPattern)
class EmailPatternAdmin(ModelAdmin):
    list_display = ('library', 'pattern', )
    search_fields = ('library__name',)

@register(models.BadUsernamePattern)
class EmailPatternAdmin(ModelAdmin):
    list_display = ('pattern', 'last')
