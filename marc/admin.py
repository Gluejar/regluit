from django.apps import apps
from django.contrib.admin import ModelAdmin, site
from django.forms import ModelForm

from selectable.forms import AutoCompleteSelectWidget,AutoCompleteSelectField

from .models import MARCRecord, EDITION_MODEL
from .lookups import EditionLookup, OwnerLookup



class MARCRecordAdminForm(ModelForm):
    edition = AutoCompleteSelectField(
            EditionLookup,
            widget=AutoCompleteSelectWidget(EditionLookup),
            required=True,
    )
    user = AutoCompleteSelectField(
            OwnerLookup,
            widget=AutoCompleteSelectWidget(OwnerLookup),
            required=True,
        )
    class Meta(object):
        model = MARCRecord
        exclude = ()

class MARCRecordAdmin(ModelAdmin):
    list_display = ('edition', 'user')
    date_hierarchy = 'created'
    form = MARCRecordAdminForm

site.register(MARCRecord, MARCRecordAdmin)
