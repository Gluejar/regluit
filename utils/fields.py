import zipfile
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat

class EpubFileField(forms.FileField):
    """
    does some epub checking; currently only checks its a zip:
    """
    def clean(self, data, initial=None):        
        data = super(EpubFileField, self).clean(data, initial)
        if data.name and not zipfile.is_zipfile(data.file):
            raise forms.ValidationError(_('%s is not a valid EPUB file' % data.name) )
        return data
