import re
from django.conf.global_settings import LANGUAGES

lang2code = dict([(lang[1].lower(), lang[0]) for lang in LANGUAGES])
code2lang = dict(LANGUAGES)
iso639 = re.compile(r'^[a-z][a-z][a-z]?$')


def get_language_code(language):
    if language is None or not language:
        return ''
    language = language.lower().strip()
    language = sep.split(language)[0].strip()
    if language in code2lang:
        return language

    # language names (english)
    if language in lang2code:
        return lang2code.get(language)

    # mispellings and language names
    if language in EXTRA_LANG_MAP:
        return EXTRA_LANG_MAP.get(language)

    # accept 2 and 3 letter codes
    if iso639.match(language):
        return language
    return ''

# let's do a mapping of the DOAB languages into the language codes used
# mostly, we just handle mispellings
# also null -> xx
sep = re.compile(r'[ ;^,/\|\'\"\]\[\t\n\r\-]+')
lang_and_locale = re.compile(r'^[a-z][a-z]\-[A-Z][A-Z]$')


# mispellings and non-english language names
EXTRA_LANG_MAP = dict([
    (u'chinese', 'de'),
    (u'deutsch', 'de'),
    (u'eng', 'en'),
    (u'engli', 'en'),
    (u'englilsh', 'en'),
    (u'englilsh', 'en'),
    (u'englisch', 'en'),
    (u'espanol', 'es'),
    (u'ger', 'de'),
    (u'fra', 'fr'),
    (u'fre', 'fr'),
    (u'francese', 'fr'),
    (u'ita', 'it'),
    (u'itali', 'it'),
    (u'italiano', 'it'),
    (u'norwegian', 'no'),
    (u'por', 'pt'),
    (u'portugese', 'pt'),
    (u'slovene', 'sl'),
    (u'spa', 'es'),
    (u'spagnolo', 'es'),
])

def lang_to_language_code(lang):
    if lang is None:
        return ''
    lang = lang.strip()

    #get codes like en-US
    if lang_and_locale.match(lang):
        return lang

    # get first item of lists
    for langitem in sep.split(lang):
        if langitem:
            lang = langitem
            continue

    code = get_language_code(lang)
    if code:
        return code
    return ''
    