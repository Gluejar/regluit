from django.core.management.base import BaseCommand

import re
import requests
from bs4 import BeautifulSoup
from regluit.core.models import Edition
from regluit.core.loaders.doab import store_doab_cover

to_fix = ['16198',  '16199',  '16201',  '16202',  '16204',  '16205',  '16206',  '16207',  '16208',  '16209',  '16210',  '16213',  '16279',  '16287',  '16302',  '17116',  '17117',  '17121',  '17129',  '17149',  '17154',  '19501',  '20186',  '20238',  '20280',  '20395',  '20447',  '20504',  '20706',  '20750',  '21317',  '21319',  '21332',  '21338',  '21343',  '21345',  '21348',  '21356',  '21643',  '21814',  '23509',  '23510',  '23516',  '23517',  '23518',  '23521',  '23523',  '23593',  '23596',  '24216',  '24282',  '24587',  '24865',  '24867',  '25496',  '25497',  '25655',  '26181',  '26308',  '26508',  '26509',  '26510',  '26511',  '26512',  '26513',  '26514',  '26515',  '26516',  '26517',  '26518',  '26523',  '26524',  '26710',  '26995',  '31899',  '31902',  '31908',  '31924',  '31930',  '31933',  '32327',  '44061']
COVER_PATTERN = re.compile(r'doabooks.org/doab\?func=cover\&rid=(\d+)')
    

class Command(BaseCommand):
    help = "fix bad covers for doab"
    
    def add_arguments(self, parser):
        parser.add_argument('doab', nargs='?', type=str, default='', help="doab to fix")

    def handle(self, doab, **options):
        if doab == 'list':
            for doab_id in to_fix:
                self.fix_doab_cover(doab_id)
            return
        self.fix_doab_cover(doab)

    def fix_doab_cover(self, doab):
        eds = Edition.objects.filter(cover_image__contains='amazonaws.com/doab/%s/cover' % doab)
    
        resp = requests.get('https://unglueit-files.s3.amazonaws.com/doab/%s/cover' % doab)
        if resp.status_code == 200 and 'text/html' in resp.headers['Content-Type']:
            doc = BeautifulSoup(resp.content, 'lxml')
            link = doc.find('a')
            if link:
                self.stdout.write(link['href'])
                new_doab = COVER_PATTERN.search(link['href'])
                if new_doab:
                    (cover_url, new_cover) = store_doab_cover(new_doab.group(1), redo=True)
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
