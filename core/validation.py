# encoding: utf-8
'''
methods to validate and clean identifiers
'''
import re
import datetime
import logging

from dateutil.parser import parse
from PyPDF2 import PdfFileReader

from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _

from regluit.pyepub import EPUB
from regluit.mobi import Mobi
from .isbn import ISBN

logger = logging.getLogger(__name__)

ID_VALIDATION = {
    'http': (re.compile(r"(https?|ftp)://(-\.)?([^\s/?\.#]+\.?)+(/[^\s]*)?$",
                        flags=re.IGNORECASE|re.S),
             "The Web Address must be a valid http(s) URL."),
    'isbn':  (u'^([\\dxX \\-–—‐,;]+|delete)$', #includes unicode hyphen, endash and emdash
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
    'oapn': (r'^(\d{1,8}|delete)$',
             "The OAPEN ID must be 1-8 digits."),
}

def isbn_cleaner(value):
    if not value:
        raise ValidationError('no identifier value found')
    elif value == 'delete':
        return value
    isbn = ISBN(value)
    if isbn.error:
        raise ValidationError(isbn.error)
    isbn.validate()
    return isbn.to_string()

def olwk_cleaner(value):
    if not value == 'delete' and value.startswith('/works/'):
        value = '/works/{}'.format(value)
    return value

doi_match = re.compile(r'10\.\d+/\S+')

def doi_cleaner(value):
    if not value == 'delete' and not value.startswith('10.'):
        try:
            return doi_match.search(value).group(0)
        except AttributeError:
            return ''
    return value

ID_MORE_VALIDATION = {
    'isbn': isbn_cleaner,
    'olwk': olwk_cleaner,
    'doi': doi_cleaner,
}

def identifier_cleaner(id_type, quiet=False):
    if ID_VALIDATION.has_key(id_type):
        (regex, err_msg) = ID_VALIDATION[id_type]
        extra = ID_MORE_VALIDATION.get(id_type, None)
        if isinstance(regex, (str, unicode)):
            regex = re.compile(regex)
        def cleaner(value):
            if not value:
                return None
            try:
                if regex.match(value):
                    if extra:
                        value = extra(value)
                    return value
                else:
                    raise ValidationError(err_msg)
            except ValidationError as ve:
                if quiet:
                    return None
                else:
                    raise ve
        return cleaner
    return lambda value: value

def test_file(the_file, fformat):
    if the_file and the_file.name:
        if fformat == 'epub':
            try:
                book = EPUB(the_file.file)
            except Exception as e:
                logger.exception(e)
                raise ValidationError(_('Are you sure this is an EPUB file?: %s' % e))
        elif fformat == 'mobi':
            try:
                book = Mobi(the_file.file)
                book.parse()
            except Exception as e:
                logger.exception(e)
                #raise ValidationError(_('Are you sure this is a MOBI file?: %s' % e))
                raise e
        elif fformat == 'pdf':
            try:
                PdfFileReader(the_file.file)
            except Exception as e:
                logger.exception(e)
                raise ValidationError(_('%s is not a valid PDF file' % the_file.name))
    return True

def valid_xml_char_ordinal(c):
    codepoint = ord(c)
    # conditions ordered by presumed frequency
    return (
        0x20 <= codepoint <= 0xD7FF or
        codepoint in (0x9, 0xA, 0xD) or
        0xE000 <= codepoint <= 0xFFFD or
        0x10000 <= codepoint <= 0x10FFFF
        )

def valid_subject(subject_name):
    if len(subject_name) > 200:
        return False
    num_commas = 0
    for c in subject_name:
        if not valid_xml_char_ordinal(c):
            return False
        if c == ',':
            num_commas += 1
            if num_commas > 2:
                return False
    if len(subject_name.split('--')) > 6:
        return False
    if len(subject_name.split('. ')) > 4:
        return False
    return True

reverse_name_comma = re.compile(r',(?! *Jr[\., ])')

def unreverse_name(name):
    name = name.strip('.')
    if not reverse_name_comma.search(name):
        return name
    (last, rest) = name.split(',', 1)
    if not ',' in rest:
        return '%s %s' % (rest.strip(), last.strip())
    (first, rest) = rest.split(',', 1)
    return '%s %s, %s' % (first.strip(), last.strip(), rest.strip())

def authlist_cleaner(authlist):
    ''' given a author string or list of author strings, checks that the author string
        is not a list of author names and that no author is repeated'''
    if isinstance(authlist, str):
        authlist = [authlist]
    cleaned = []
    for auth in authlist:
        for cleaned_auth in auth_cleaner(auth):
            if cleaned_auth not in cleaned:
                cleaned.append(cleaned_auth)
    return cleaned

# Match comma but not ", Jr"
comma_list_delim = re.compile(r',(?! *Jr[\., ])')
spaces = re.compile(r'\s+')
_and_ = re.compile(r',? (and|\&) ')
semicolon_list_delim = re.compile(r'[\;|\&]')
reversed_name = re.compile(r'(de |la |los |von |van )*\w+, \w+.?( \w+.?)?(, Jr\.?)?')

def auth_cleaner(auth):
    ''' given a author string checks that the author string
        is not a list of author names'''
    cleaned = []
    if ';' in auth or reversed_name.match(auth):
        authlist = semicolon_list_delim.split(auth)
        authlist = [unreverse_name(name) for name in authlist]
    else:
        auth = _and_.sub(',', auth)
        authlist = comma_list_delim.split(auth)
    for auth in authlist:
        cleaned.append(spaces.sub(' ', auth.strip()))
    return cleaned

MATCHYEAR = re.compile(r'(1|2)\d\d\d')
MATCHYMD = re.compile(r'(1|2)\d\d\d-\d\d-\d\d')

def validate_date(date_string):
    ymd = MATCHYMD.search(date_string)
    if ymd:
        return ymd.group(0)
    try:
        date = parse(date_string.strip(), default=datetime.date(999, 1, 1))
        if date.year != 999:
            return date.strftime('%Y')
    except ValueError:
        year = MATCHYEAR.search(date_string)
        if year:
            return year.group(0)
        return ''
