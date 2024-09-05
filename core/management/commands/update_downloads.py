import os
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import F, Sum

from regluit.core.models import Ebook

DOWNLOAD_LOGFILE = settings.LOGGING['handlers']['downloads']['filename']

class Command(BaseCommand):
    '''add logged downloads to ebook objects'''
    help = "add logged downloads to ebook objects"
    
    def handle(self, **options):
        dls = {}
        date_format = "%Y-%m-%d"

        this_mo = datetime.today().month
        last_month = this_mo - 1
        year = datetime.today().year
        if last_month <= 0:
            last_month = last_month + 12
        total = 0
        with open(DOWNLOAD_LOGFILE,'r') as logfile:
            for line in logfile.readlines():
                (date, time, colon, ebook) = line.split()
                month = datetime.strptime(date, date_format).date().month
                if month == last_month:
                    dls[ebook] = dls.get(ebook, 0) + 1
                    total += 1

        downloads = Ebook.objects.aggregate(total=Sum('download_count'))['total']
        self.stdout.write(f'old count: {downloads} downloads')
        self.stdout.write(f'logging {total} downloads for len(dls) ebooks')
        
        for key in dls.keys():
            if dls[key] > settings.DOWNLOAD_LOGS_MAX:
                self.stdout.write(f'{dls[key]} downloads for ebook {key} discarded.' )
                continue
            try:
                Ebook.objects.filter(id=key).update(download_count=F('download_count') + dls[key])
            except Ebook.object.DoesNotExist:
                self.stdout.write(f'ebook {key} not found')

        downloads = Ebook.objects.aggregate(total=Sum('download_count'))['total']
        self.stdout.write(f'new count: {downloads} downloads')
