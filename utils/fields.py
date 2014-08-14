import zipfile
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat
from regluit.core.isbn import ISBN

class EpubFileField(forms.FileField):
    """
    does some epub checking; currently only checks its a zip:
    """
    def clean(self, data, initial=None):        
        data = super(EpubFileField, self).clean(data, initial)
        if data.name and not zipfile.is_zipfile(data.file):
            raise forms.ValidationError(_('%s is not a valid EPUB file' % data.name) )
        return data

class ISBNField(forms.CharField):
    def to_python(self, value):
        value=super(ISBNField,self).to_python(value)
        if not value:
            return ''
        elif value == 'delete':
            return value
        self.isbn=ISBN(value)
        if self.isbn.error:
            raise forms.ValidationError(self.isbn.error)
        self.isbn.validate()
        return self.isbn.to_string()
        
        