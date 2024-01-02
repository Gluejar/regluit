from django.core.management.base import BaseCommand

import re
import requests
from regluit.core.models import Edition, Work
from regluit.core.loaders.doab import store_doab_cover

to_fix = [
]
missing = [
]

class Command(BaseCommand):
    """ To repair covers, will need a new refresh_cover method"""
    help = "fix bad covers"
    
    def add_arguments(self, parser):
        parser.add_argument('doab', nargs='?', default='', help="doab to fix")

    def handle(self, doab, **options):
        if doab == 'mangled':
            self.fix_mangled_covers()
        elif doab == 'list':
            for doab_id in to_fix:
                self.fix_doab_cover(doab_id)
            return True
        elif doab == 'null':
            no_cover_doab = Work.objects.filter(identifiers__type='doab').exclude(editions__cover_image__isnull=False)
            for work in no_cover_doab:
                cover_url = self.refresh_cover(work.doab)
                if cover_url:
                    for e in work.editions.all():
                        e.cover_image = cover_url
                        e.save()
                    self.stdout.write(f'added cover for {work.doab}')
        else:
            return self.fix_doab_cover(doab)
        return False

    def fix_doab_cover(self, doab):
        eds = Edition.objects.filter(cover_image__contains=doab)
    
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
        self.stdout.write('fixed %s mangled covers' % eds.count())
        eds = Edition.objects.exclude(cover_image__startswith='http').filter(cover_image__regex='.')
        for ed in eds:
            ed.cover_image = ''
            ed.save()
        self.stdout.write('fixed %s file covers' % eds.count())
        fixed = 0
        for cover in missing:
            eds = Edition.objects.filter(cover_image=cover)
            for ed in eds:
                ed.cover_image = ''
                ed.save()
                fixed += 1
        self.stdout.write('fixed %s file covers' % fixed)

    def refresh_cover(self, doab):
        new_cover, created = store_doab_cover(doab, redo=True)
        return new_cover
