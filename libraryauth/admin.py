from django import forms
from django.contrib.admin import ModelAdmin, site
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


class LibraryAdmin(ModelAdmin):
    list_display = ('user', )
    form = LibraryAdminForm
    search_fields = ['user__username']

class BlockAdmin(ModelAdmin):
    list_display = ('library', 'lower', 'upper',)
    search_fields = ('library__name', 'lower', 'upper',)

class CardPatternAdmin(ModelAdmin):
    list_display = ('library', 'pattern', 'checksum',)
    search_fields = ('library__name', )

class EmailPatternAdmin(ModelAdmin):
    list_display = ('library', 'pattern', )
    search_fields = ('library__name',)

site.register(models.Library, LibraryAdmin)
site.register(models.Block, BlockAdmin)
site.register(models.CardPattern, CardPatternAdmin)
site.register(models.EmailPattern, EmailPatternAdmin)
