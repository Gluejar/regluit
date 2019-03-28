from django.core.management.base import BaseCommand

from regluit.core.models import Work
from regluit.utils.lang import lang_to_language_code, lang_and_locale, iso639

iso639 = r'^[a-z][a-z][a-z]?$'
lang_and_locale = r'^[a-z][a-z]\-[A-Z][A-Z]$'

class Command(BaseCommand):
    '''remove works and editions without titles'''
    help = "remove works and editions without titles"
    
    def handle(self, **options):
        badworks = Work.objects.exclude(language__regex=iso639)
        badworks = badworks.exclude(language__regex=lang_and_locale)
        self.stdout.write('{} works to fix'.format(badworks.count()))
        for work in badworks:
            language = lang_to_language_code(work.language)
            work.language = language if language else 'xx'
            work.save()
