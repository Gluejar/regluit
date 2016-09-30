from django import forms

from selectable.forms import (
    AutoCompleteSelectWidget,
    AutoCompleteSelectField
)

from regluit.core.lookups import EditionLookup

class MARCUploadForm(forms.Form):
    edition = AutoCompleteSelectField(
            EditionLookup,
            label='Edition',
            widget=AutoCompleteSelectWidget(EditionLookup),
            required=True,
            error_messages={'required': 'Please specify an edition.'},
        )    
    file = forms.FileField(label='Select a MARCXML file.')
    source = forms.ChoiceField(label='This file is ...', choices=[
       ( 'loc' , 'from Library of Congress (print)'),
       ( 'raw' , 'prepared for Unglue.it'),
    ])
