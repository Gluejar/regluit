from __future__ import print_function
from django.core.management.base import BaseCommand

from regluit.core.models import Work
from regluit.core.loaders.doab import update_cover_doab

class Command(BaseCommand):
    help = "make covers for doab editions with bad covers"
    
    def handle(self, **options):
        works = Work.objects.filter(identifiers__type='doab').distinct()
        print('checking {} works with doab'.format(works.count()))
        num = 0
        for work in works:
            if not work.cover_image_thumbnail():
                update_cover_doab(work.doab, work.preferred_edition, store_cover=True)
                #print(work.doab)
                num += 1
                if num % 10 == 0:
                    print('{} doab covers updated'.format(num))
                    #break
        print('Done: {} doab covers updated'.format(num))