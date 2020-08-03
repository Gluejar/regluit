from django.core.management.base import BaseCommand

from regluit.core.models import EbookFile, Ebook
from regluit.core.loaders.utils import get_soup

class Command(BaseCommand):

    def handle(self, **options):
        prov = 'ebooks.epublishing.ekt.gr'
        for ebook in Ebook.objects.filter(provider=prov, format='online'):
            print(ebook.url)
            doc = get_soup(ebook.url)
            if doc:
                objs = doc.select('.chapters a.cmp_download_link[href]')
                for obj in objs:
                    for ebf in EbookFile.objects.filter(source=obj['href']):
                        bad_ebook = ebf.ebook
                        try:
                            ebf.file.delete()
                        except:
                            pass
                        ebf.delete()
                        bad_ebook.delete()
