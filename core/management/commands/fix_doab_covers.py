from django.core.management.base import BaseCommand

import re
import requests
from regluit.core.models import Edition

to_fix = []
    

class Command(BaseCommand):
    """ To repair covers, will need a new refresh_cover method"""
    help = "fix bad covers for doab"
    
    def add_arguments(self, parser):
        parser.add_argument('doab', nargs='?', default='', help="doab to fix")

    def handle(self, doab, **options):
        if doab == 'list':
            for doab_id in to_fix:
                self.fix_doab_cover(doab_id)
            return
        self.fix_doab_cover(doab)

    def fix_doab_cover(self, doab):
        eds = Edition.objects.filter(cover_image__contains='amazonaws.com/doab/%s/cover' % doab)
    
        cover_url = self.refresh_cover(doab)
        if cover_url:
            for e in eds:
                e.cover_image = cover_url
                e.save()
                if e.cover_image_small() and e.cover_image_thumbnail():
                    self.stdout.write('fixed %s  using %s' % (doab, new_doab.group(1)))
                else:
                    self.stdout.write('bad thumbnails for %s' % new_doab.group(1))
                    return False
        return True
        self.stdout.write('removing bad cover for %s' % doab)

        for e in eds:
            e.cover_image = None
            e.save()
        return False

    def refresh_cover(self, doab):
        return False
