from django.core.management.base import BaseCommand

import re
import requests
from regluit.core.models import Edition
from regluit.core.loaders.doab_utils import doab_cover

to_fix = [
"20.500.12854/25941",
"20.500.12854/29841",
"20.500.12854/30286",
"20.500.12854/39341",
"20.500.12854/41049",
"20.500.12854/41911",
"20.500.12854/44478",
"20.500.12854/44685",
"20.500.12854/45396",
"20.500.12854/47243",
"20.500.12854/47305",
"20.500.12854/48790",
"20.500.12854/52599",
"20.500.12854/56238",
"20.500.12854/58193",
"20.500.12854/58504",
"20.500.12854/58546",
"20.500.12854/58889",
"20.500.12854/62025",
"20.500.12854/62618"
]

class Command(BaseCommand):
    """ To repair covers, will need a new refresh_cover method"""
    help = "fix bad covers for doab"
    
    def add_arguments(self, parser):
        parser.add_argument('doab', nargs='?', default='', help="doab to fix")

    def handle(self, doab, **options):
        if doab == 'mangled':
            self.fix_mangled_covers()
        if doab == 'list':
            for doab_id in to_fix:
                self.fix_doab_cover(doab_id)
            return
        self.fix_doab_cover(doab)

    def fix_doab_cover(self, doab):
        eds = Edition.objects.filter(cover_image__contains='amazonaws.com/doab/%s' % doab)
    
        cover_url = self.refresh_cover(doab)
        if cover_url:
            for e in eds:
                e.cover_image = cover_url
                e.save()
                if e.cover_image_small() and e.cover_image_thumbnail():
                    self.stdout.write('fixed %s  using %s' % (doab, cover_url))
                else:
                    self.stdout.write('bad thumbnails for %s' % cover_url)
                    return False
        return True
        self.stdout.write('removing bad cover for %s' % doab)

        for e in eds:
            e.cover_image = None
            e.save()
        return False

    def fix_mangled_covers(self):
        eds = Edition.objects.filter(cover_image__contains='amazonaws.comdoab')
        for ed in eds:
            cover_url = ed.cover_image.replace('amazonaws.comdoab', 'amazonaws.com/doab')
            ed.cover_image = cover_url
            ed.save()
        self.stdout.write('fixed %s covers' % eds.count())

    def refresh_cover(self, doab):
        return doab_cover(doab)
