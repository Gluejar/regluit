from django.core.management.base import BaseCommand

from regluit.core.models import Work
from regluit.core.loaders.doab import update_cover_doab

class Command(BaseCommand):
    help = "make covers for doab editions"
    
    def handle(self, **options):

        works = Work.objects.filter(selected_edition__isnull=False, selected_edition__cover_image__isnull=True)
        #.filter(selected_edition__isnull=False, selected_edition__cover_image__isnull=True)
        #.exclude(selected_edition__identifiers__type='goog')
        added = 0
        for work in works:
            if work.doab and work.selected_edition.googlebooks_id == '':
                update_cover_doab(work.doab, work.selected_edition)
                added += 1
        print('added {} covers'.format(added))
