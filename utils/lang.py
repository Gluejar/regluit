from django.conf.global_settings import LANGUAGES

lang2code = dict([ (lang[1].lower(), lang[0]) for lang in LANGUAGES ])
code2lang = dict(LANGUAGES)

def get_language_code(language):
    language = language.lower().strip()
    if language in code2lang:
        return language
    return lang2code.get(language, '')
