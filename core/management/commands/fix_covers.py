from django.core.management.base import BaseCommand

import re
import requests
from regluit.core.models import Edition, Work
from regluit.core.loaders.doab import store_doab_cover

to_fix = [
"20.500.12854/107832",
"20.500.12854/107837",
"20.500.12854/107840",
"20.500.12854/107842",
"20.500.12854/107857",
"20.500.12854/107861",
"20.500.12854/107862",
"20.500.12854/107865",
"20.500.12854/107868",
"20.500.12854/107884",
"20.500.12854/107893",
"20.500.12854/107894",
"20.500.12854/107896",
"20.500.12854/107909",
"20.500.12854/107914",
"20.500.12854/107920",
"20.500.12854/107921",
"20.500.12854/107928",
"20.500.12854/107935",
"20.500.12854/107938",
"20.500.12854/107952",
"20.500.12854/114287",
"20.500.12854/114376",
"20.500.12854/114378",
"20.500.12854/114380",
"20.500.12854/114381",
"20.500.12854/114383",
"20.500.12854/115842",
"20.500.12854/115843",
"20.500.12854/115844",
"20.500.12854/115976",
"20.500.12854/115991",
"20.500.12854/116099",
"20.500.12854/116126",
"20.500.12854/116130",
"20.500.12854/116164",
"20.500.12854/116175",
"20.500.12854/116471",
"20.500.12854/116486",
"20.500.12854/121414",
"20.500.12854/121415",
"20.500.12854/121640",
"20.500.12854/136546",
"20.500.12854/41911",
"20.500.12854/47305",
"20.500.12854/58546",
"20.500.12854/76719",
"20.500.12854/88320",
"20.500.12854/88413",
"20.500.12854/88414",
"20.500.12854/88453",
"20.500.12854/88479",
"20.500.12854/88655",
"20.500.12854/88656",
"20.500.12854/88657",
"20.500.12854/88659",
"20.500.12854/88660",
"20.500.12854/88661",
"20.500.12854/88662",
"20.500.12854/88663",
"20.500.12854/88664",
"20.500.12854/88665",
"20.500.12854/88666",
"20.500.12854/88667",
"20.500.12854/88668",
"20.500.12854/88669",
"20.500.12854/88670",
"20.500.12854/88671",
"20.500.12854/88675",
"20.500.12854/88677",
"20.500.12854/88678",
"20.500.12854/88679",
"20.500.12854/88680",
"20.500.12854/88681",
"20.500.12854/88683",
"20.500.12854/88686",
"20.500.12854/88687",
"20.500.12854/89178",
"20.500.12854/89252",
"20.500.12854/89255",
"20.500.12854/89257",
"20.500.12854/89260",
"20.500.12854/89265",
"20.500.12854/89441",
"20.500.12854/89490",
"20.500.12854/89496",
"20.500.12854/89498",
"20.500.12854/89514",
"20.500.12854/91350",
"20.500.12854/96212",
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
