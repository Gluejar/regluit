import re

from ckeditor.widgets import CKEditorWidget

from django import forms
from django.conf.global_settings import LANGUAGES
from regluit.utils.text import sanitize_line, remove_badxml
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
from regluit.core.models import Edition
from regluit.core.parameters import (
    AGE_LEVEL_CHOICES,
    TEXT_RELATION_CHOICES,
)
from regluit.utils.fields import ISBNField

CREATOR_RELATIONS = (
    ('aut', 'Author'),
    ('edt', 'Editor'),
    ('trl', 'Translator'),
    ('ill', 'Illustrator'),
    ('dsr', 'Designer'),
    ('aui', 'Author of Introduction'),
)

nulls = [False, 'delete', '']

bisac_headings = BisacHeading.objects.all()

class EditionForm(forms.ModelForm):
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

    isbn = ISBNField(
        label=_("ISBN"),
        max_length=17,
        required = False,
        help_text = _("13 digits, no dash."),
        error_messages = {
            'invalid': _("This must be a valid ISBN-13."),
        }
    )
    goog = forms.RegexField(
        label=_("Google Books ID"),
        max_length=12,
        regex=r'^([a-zA-Z0-9\-_]{12}|delete)$',
        required = False,
        help_text = _("12 alphanumeric characters, dash or underscore, case sensitive."),
        error_messages = {
            'invalid': _("This value must be 12 alphanumeric characters, dash or underscore."),
        }
    )
    gdrd = forms.RegexField(
        label=_("GoodReads ID"),
        max_length=8,
        regex=r'^(\d+|delete)$',
        required = False,
        help_text = _("1-8 digits."),
        error_messages = {
            'invalid': _("This value must be 1-8 digits."),
        }
    )
    thng = forms.RegexField(
        label=_("LibraryThing ID"),
        max_length=8,
        regex=r'(^\d+|delete)$',
        required = False,
        help_text = _("1-8 digits."),
        error_messages = {
            'invalid': _("This value must be 1-8 digits."),
        }
    )
    oclc = forms.RegexField(
        label=_("OCLCnum"),
        regex=r'^(\d\d\d\d\d\d\d\d\d*|delete)$',
        required = False,
        help_text = _("8 or more digits."),
        error_messages = {
            'invalid': _("This value must be 8 or more digits."),
        }
    )
    http = forms.RegexField(
        label=_("HTTP URL"),
        # https://mathiasbynens.be/demo/url-regex
        regex=re.compile(r"(https?|ftp)://(-\.)?([^\s/?\.#]+\.?)+(/[^\s]*)?$",
                         flags=re.IGNORECASE|re.S ),
        required = False,
        help_text = _("no spaces of funny stuff."),
        error_messages = {
            'invalid': _("This value must be a valid http(s) URL."),
        }
    )
    doi = forms.RegexField(
        label=_("DOI"),
        regex=r'^(https?://dx\.doi\.org/|https?://doi\.org/)?(10\.\d+/\S+|delete)$',
        required = False,
        help_text = _("starts with '10.' or 'https://doi.org'"),
        error_messages = {
            'invalid': _("This value must be a valid DOI."),
        }
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
        has_isbn = self.cleaned_data.get("isbn", False) not in nulls
        has_oclc = self.cleaned_data.get("oclc", False) not in nulls
        has_goog = self.cleaned_data.get("goog", False) not in nulls
        has_http = self.cleaned_data.get("http", False) not in nulls
        has_doi = self.cleaned_data.get("doi", False) not in nulls
        try:
            has_id = self.instance.work.identifiers.all().count() > 0
        except AttributeError:
            has_id = False
        if (not has_id and
            not has_isbn and
            not has_oclc and
            not has_goog and
            not has_http and
            not has_doi):
            raise forms.ValidationError(
                _("There must be either an ISBN, a DOI, a URL or an OCLC number.")
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

