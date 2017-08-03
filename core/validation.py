# encoding: utf-8
'''
methods to validate and clean identifiers
'''
import re
from django.forms import ValidationError
from .isbn import ISBN

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
    'gdrd': (r'^(\d{1,8}|delete)$', 
        "The Goodreads ID must be 1-8 digits."),
    'thng': (r'(^\d{1,8}|delete)$', 
        "The LibraryThing ID must be 1-8 digits."),
    'olwk': (r'^(/works/\)?OLd{1,8}W|delete)$', 
        "The Open Library Work ID looks like 'OL####W'."),
    'glue': (r'^(\d{1,6}|delete)$', 
        "The Unglue.it ID must be 1-6 digits."),
    'ltwk': (r'^(\d{1,8}|delete)$', 
        "The LibraryThing work ID must be 1-8 digits."),
}

def isbn_cleaner(value):
    if value == 'delete':
        return value
    if not value:
        raise forms.ValidationError('no identifier value found')
    elif value == 'delete':
        return value
    isbn=ISBN(value)
    if isbn.error:
        raise forms.ValidationError(isbn.error)
    isbn.validate()
    return isbn.to_string()

def olwk_cleaner(value):
    if not value == 'delete' and value.startswith('/works/'):
        value = '/works/{}'.format(value)
    return value

doi_match = re.compile( r'10\.\d+/\S+')

def doi_cleaner(value):
    if not value == 'delete' and not value.startswith('10.'):
        return doi_match.match(value).group(0)
    return value
        
ID_MORE_VALIDATION = {
    'isbn': isbn_cleaner,
    'olwk': olwk_cleaner,
    'olwk': doi_cleaner,
}

def identifier_cleaner(id_type):
    if ID_VALIDATION.has_key(id_type):
        (regex, err_msg) = ID_VALIDATION[id_type]
        extra = ID_MORE_VALIDATION.get(id_type, None)
        if isinstance(regex, (str, unicode)):
            regex = re.compile(regex)
        def cleaner(value):
            if not value:
                return None
            if regex.match(value):
                if extra:
                    value = extra(value)
                return value
            else:
                raise ValidationError(err_msg)
        return cleaner
    return lambda value: value

