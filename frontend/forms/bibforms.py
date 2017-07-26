# encoding: utf-8
'''
forms for bib models
'''
import re

from ckeditor.widgets import CKEditorWidget

from django import forms
from django.conf.global_settings import LANGUAGES
from django.utils.translation import ugettext_lazy as _

from selectable.forms import (
    AutoCompleteSelectWidget,
    AutoCompleteSelectField
)
from regluit.core.lookups import (
    WorkLookup,
    PublisherNameLookup,
    SubjectLookup,
    EditionNoteLookup,
)
from regluit.bisac.models import BisacHeading
from regluit.core.isbn import ISBN
from regluit.core.models import Edition, Identifier
from regluit.core.parameters import (
    AGE_LEVEL_CHOICES,
    ID_CHOICES,
    TEXT_RELATION_CHOICES,
)
from regluit.utils.fields import ISBNField
from regluit.utils.text import sanitize_line, remove_badxml

CREATOR_RELATIONS = (
    ('aut', 'Author'),
    ('edt', 'Editor'),
    ('trl', 'Translator'),
    ('ill', 'Illustrator'),
    ('dsr', 'Designer'),
    ('aui', 'Author of Introduction'),
)

NULLS = [False, 'delete', '']

bisac_headings = BisacHeading.objects.all()

ID_VALIDATION = {
    'http': (re.compile(r"(https?|ftp)://(-\.)?([^\s/?\.#]+\.?)+(/[^\s]*)?$",
         flags=re.IGNORECASE|re.S ), 
         "The Web Address must be a valid http(s) URL."),  
    'isbn':  (r'^([\dxX\-–— ]+|delete)$', 
        "The ISBN must be a valid ISBN-13."),
    'doab': (r'^(\d{1,6}|delete)$', 
        "The value must be 1-6 digits."),
    'gtbg': (r'^(\d{1,6}|delete)$',
        "The Gutenberg number must be 1-6 digits."),
    'doi': (r'^(https?://dx\.doi\.org/|https?://doi\.org/)?(10\.\d+/\S+|delete)$', 
        "The DOI value must be a valid DOI."),
    'oclc': (r'^(\d{8,12}|delete)$', 
        "The OCLCnum must be 8 or more digits."),
    'goog': (r'^([a-zA-Z0-9\-_]{12}|delete)$', 
        "The Google id must be 12 alphanumeric characters, dash or underscore."),
    'olib': (r'^(\d{1,8}|delete)$',
        "The Open Library ID must be 1-8 digits."),
    'gdrd': (r'^(\d{1,8}|delete)$', 
        "The Goodreads ID must be 1-8 digits."),
    'thng': (r'(^\d{1,8}|delete)$', 
        "The LibraryThing ID must be 1-8 digits."),
    'olwk': (r'^(\d{1,8}|delete)$', 
        "The Open Library ID must be 1-8 digits."),
    'glue': (r'^(\d{1,6}|delete)$', 
        "The Unglue.it ID must be 1-6 digits."),
    'ltwk': (r'^(\d{1,8}|delete)$', 
        "The LibraryThing ID must be 1-8 digits."),
}

def isbn_cleaner(value):
    if not value:
        raise forms.ValidationError('no identifier value found')
    elif value == 'delete':
        return value
    isbn=ISBN(value)
    if isbn.error:
        raise forms.ValidationError(isbn.error)
    isbn.validate()
    return isbn.to_string()
        
ID_MORE_VALIDATION = {
    'isbn': isbn_cleaner
}

def identifier_cleaner(id_type):
    print id_type
    if ID_VALIDATION.has_key(id_type):
        (regex, err_msg) = ID_VALIDATION[id_type]
        extra = ID_MORE_VALIDATION.get(id_type, None)
        if isinstance(regex, (str, unicode)):
            regex = re.compile(regex)
        def cleaner(value):
            if regex.match(value):
                if extra:
                    value = extra(value)
                return value
            else:
                raise forms.ValidationError(err_msg)
        return cleaner
    return lambda value: value

class IdentifierForm(forms.ModelForm):
    id_type = forms.ChoiceField(label='Identifier Type', choices=ID_CHOICES)
    id_value = forms.CharField(label='Identifier Value', widget=forms.TextInput(attrs={'size': 60}))
    identifier = None
    
    def clean(self):
        id_type = self.cleaned_data['id_type']
        id_value = self.cleaned_data['id_value'].strip()
        identifier = Identifier.objects.filter(type=id_type, value=id_value)
        if identifier:
            self.identifier = identifier[0]
            return self.cleaned_data
        
        self.cleaned_data['value'] = identifier_cleaner(id_type)(id_value)
        return self.cleaned_data
                        
    class Meta:
        model = Identifier
        fields = ('id_type', 'id_value')
        widgets = {
                'id_value': forms.TextInput(attrs={'size': 40}),
        }

class EditionForm(forms.ModelForm):
    '''
    form for bibliographic data (both editions and works
    '''
    add_author = forms.CharField(max_length=500, required=False)
    add_author_relation = forms.ChoiceField(choices=CREATOR_RELATIONS, initial=('aut', 'Author'))
    add_subject = AutoCompleteSelectField(
        SubjectLookup,
        widget=AutoCompleteSelectWidget(SubjectLookup, allow_new=True),
        label='Keyword',
        required=False,
        )
    add_related_work =  AutoCompleteSelectField(
        WorkLookup,
        widget=AutoCompleteSelectWidget(WorkLookup, allow_new=False, attrs={'size': 40}),
        label='Related Work',
        required=False,
    )
    add_work_relation = forms.ChoiceField(
        choices=TEXT_RELATION_CHOICES,
        initial=('translation', 'translation'),
        required=False,
    )

    bisac = forms.ModelChoiceField( bisac_headings, required=False )

    publisher_name = AutoCompleteSelectField(
        PublisherNameLookup,
        label='Publisher Name',
        widget=AutoCompleteSelectWidget(PublisherNameLookup,allow_new=True),
        required=False,
        allow_new=True,
    )

    id_type = forms.ChoiceField(label='Identifier Type', choices=ID_CHOICES)
    id_value = forms.CharField(label='Identifier Value', widget=forms.TextInput(attrs={'size': 60}))
    language = forms.ChoiceField(choices=LANGUAGES)
    age_level = forms.ChoiceField(choices=AGE_LEVEL_CHOICES, required=False)
    description = forms.CharField( required=False, widget=CKEditorWidget())
    coverfile = forms.ImageField(required=False)
    note = AutoCompleteSelectField(
        EditionNoteLookup,
        widget=AutoCompleteSelectWidget(EditionNoteLookup, allow_new=True),
        label='Edition Note',
        required=False,
        allow_new=True,
        )
    def __init__(self,  *args, **kwargs):
        super(EditionForm, self).__init__(*args, **kwargs)
        self.relators = []
        if self.instance:
            for relator in self.instance.relators.all():
                select = forms.Select(choices=CREATOR_RELATIONS).render(
                    'change_relator_%s' % relator.id,
                    relator.relation.code
                )
                self.relators.append({'relator':relator, 'select':select})

    def clean_doi(self):
        doi = self.cleaned_data["doi"]
        if doi and doi.startswith("http"):
            return doi.split('/', 3)[3]
        return doi

    def clean_title(self):
        return sanitize_line(self.cleaned_data["title"])

    def clean_add_author(self):
        return sanitize_line(self.cleaned_data["add_author"])

    def clean_description(self):
        return remove_badxml(self.cleaned_data["description"])

    def clean(self):
        id_type = self.cleaned_data['id_type']
        id_value = self.cleaned_data['id_value'].strip()
        identifier = Identifier.objects.filter(type=id_type, value=id_value)
        if identifier:
            err_msg = "{} is a duplicate for work #{}.".format(identifier[0], identifier[0].work.id)
            self.add_error('id_value', forms.ValidationError(err_msg))
        try:
            self.cleaned_data['value'] = identifier_cleaner(id_type)(id_value)
        except forms.ValidationError, ve:
            self.add_error('id_value', forms.ValidationError('{}: {}'.format(ve.message, id_value)))
        return self.cleaned_data

    class Meta:
        model = Edition
        exclude = ('created', 'work')
        widgets = {
                'title': forms.TextInput(attrs={'size': 40}),
                'add_author': forms.TextInput(attrs={'size': 30}),
                'add_subject': forms.TextInput(attrs={'size': 30}),
                'unglued': forms.CheckboxInput(),
                'cover_image': forms.TextInput(attrs={'size': 60}),
            }

