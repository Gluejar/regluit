from django.conf.global_settings import LANGUAGES

lang2code = dict([ (lang[1].lower(), lang[0]) for lang in LANGUAGES ])

def get_language_code(language):
    return lang2code.get(language.lower().strip(), '')
