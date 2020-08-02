from django.core.management.base import BaseCommand

from regluit.core.models import EbookFile

class Command(BaseCommand):

    def handle(self, **options):
        prov = 'editorial.uniagustiniana.edu.co'
        for ebook in Ebook.objects.filter(provider=prov, format='online'):
            print(ebook.url)
            doc = get_soup(ebook.url)
            if doc:
                objs = doc.select('.tab-content a.cmp_download_link[href]')
                for obj in objs:
                    for ebf in EbookFile.objects.filter(source=ebook.url):
                        bad_ebook = ebf.ebook
                        try:
                            ebf.file.delete()
                        except:
                            pass
                        ebf.delete()
                        bad_ebook.delete()
