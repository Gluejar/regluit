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
from regluit.core.cc import CHOICES as RIGHTS_CHOICES
from regluit.core.models import Edition, Identifier
from regluit.core.parameters import (
    AGE_LEVEL_CHOICES,
    ID_CHOICES,
    TEXT_RELATION_CHOICES,
)
from regluit.core.validation import identifier_cleaner
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

class IdentifierForm(forms.ModelForm):
    id_type = forms.ChoiceField(label='Identifier Type', choices=ID_CHOICES)
    id_value = forms.CharField(
        label='Identifier Value',
        widget=forms.TextInput(attrs={'size': 60}),
        required=False,
    )
    make_new = forms.BooleanField(
        label='There\'s no existing Identifier. ',
        required=False,
    )
    identifier = None
    
    def clean(self):
        id_type = self.cleaned_data['id_type']
        id_value = self.cleaned_data.get('id_value', '').strip()
        make_new =  self.cleaned_data.get('make_new', False)
        if not make_new:
            self.cleaned_data['id_value'] = identifier_cleaner(id_type)(id_value)
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
    id_value = forms.CharField(
        label='Identifier Value',
        widget=forms.TextInput(attrs={'size': 60}),
        required=False,
    )
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
    set_rights = forms.CharField(widget=forms.Select(choices=RIGHTS_CHOICES), required=False)
    
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

    def clean_title(self):
        return sanitize_line(self.cleaned_data["title"])

    def clean_add_author(self):
        return sanitize_line(self.cleaned_data["add_author"])

    def clean_description(self):
        return remove_badxml(self.cleaned_data["description"])

    def clean(self):
        id_type = self.cleaned_data['id_type']
        id_value = self.cleaned_data.get('id_value','').strip()
        if id_value:
            try:
                id_value = identifier_cleaner(id_type)(id_value)
                identifier = Identifier.objects.filter(type=id_type, value=id_value)
                ident = identifier[0] if identifier else None
                if not ident or not self.instance:
                    self.cleaned_data['id_value'] = id_value
                elif ident.edition_id == self.instance.id:
                    self.cleaned_data['id_value'] = id_value
                elif not ident.edition_id and ident.work_id == self.instance.work_id:
                    self.cleaned_data['id_value'] = id_value
                else:
                    if ident.edition_id:
                        err_msg = "{} is a duplicate for edition #{}.".format(id_value, ident.edition_id)
                    else:
                        err_msg = "{} is a duplicate for work #{}.".format(id_value, ident.work_id)
                    self.add_error('id_value', forms.ValidationError(err_msg))
            except forms.ValidationError, ve:
                self.add_error(
                    'id_value',
                    forms.ValidationError('{}: {}'.format(ve.message, id_value))
                )
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

