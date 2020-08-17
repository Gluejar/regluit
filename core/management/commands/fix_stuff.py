from django.core.management.base import BaseCommand

from regluit.core.models import EbookFile, Ebook
from regluit.core.loaders.soup import get_soup

class Command(BaseCommand):

    def handle(self, **options):
        for ebf in EbookFile.objects.filter(ebook__isnull=True, source__isnull=False):
            ebf.delete()
        for ebf in EbookFile.objects.filter(ebook__filesize=0):
            try:
                ebf.ebook.filesize = ebf.file.size
                ebf.ebook.save()
            except:
                pass
        for ebf in EbookFile.objects.filter(ebook__filesize__isnull=True):
            try:
                ebf.ebook.filesize = ebf.file.size
                ebf.ebook.save()
            except:
                pass
            
