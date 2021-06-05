import re

from django.core.management.base import BaseCommand

from regluit.core.models import Ebook, EbookFile


class Command(BaseCommand):
    help = "fix mdpi Ebooks"

    def handle(self, **options):
        mdpi_match = re.compile(r'https://res.mdpi.com/bookfiles/book/(\d+)(.*)\?v=\d+')

        mdpi_ebs = Ebook.objects.filter(url__startswith='https://res.mdpi.com/bookfiles/book/', url__contains="?v=")
        mdpi_ebfs = EbookFile.objects.filter(source__startswith='https://res.mdpi.com/bookfiles/book/', source__contains="?v=")
        self.stdout.write('Ebooks %s, Ebook Files %s' % (mdpi_ebs.count(), mdpi_ebfs.count()))

        done = []
        for ebf in mdpi_ebfs.order_by('-created'):
            match_ebf = mdpi_match.match(ebf.source)
            if match_ebf:
                bookno = match_ebf.group(1)
                if bookno in done:
                    continue
                else:
                    done.append(bookno)
                stem = ebf.source.split('?')[0]
                online_url = 'https://www.mdpi.com/books/pdfview/book/' + bookno
                size = ebf.ebook.filesize
        
                # change the ebook provider to unglue.it
                if ebf.ebook.provider != 'Unglue.it':
                    ebf.ebook.provider = 'Unglue.it'
                    ebf.ebook.url = ebf.file.url
                    ebf.ebook.active = True
                    ebf.ebook.save()

                # create the online ebook that should have been
                online=Ebook.objects.get_or_create(format='online', url=online_url, edition=ebf.edition,
                                            active=False, rights=ebf.ebook.rights, provider='MDPI Books')
        
                # reset ebf source
                ebf.source = online_url
                ebf.save()
        
                # check for duplicate ebfs
                for old_ebook in mdpi_ebs.filter(url__contains='/' + bookno + '/').exclude(id=ebf.id).order_by('-created'):
                    old_ebook.active = False
                    for oldebf in old_ebook.ebook_files.exclude(id=ebf.id):
                        if oldebf.file != ebf.file:
                            # save storage by deleting redundant files
                            oldebf.file.delete()
                            oldebf.file = ebf.file
                            oldebf.source = ebf.source.split('?')[0]
                            oldebf.save()
                    old_ebook.save()
        
        # now make the rest of the ebooks onlines 
        done = []
        for eb in mdpi_ebs.filter(active=True):
            match_eb = mdpi_match.match(eb.url)
            if match_eb:
                # make sure not already harvested
                if eb.ebook_files.count():
                    self.stdout.write('ebook %s already harvested' % eb.id)
                    continue
                bookno = match_eb.group(1)
                eb.active = False
                if bookno not in done:
                    done.append(bookno)
                    eb.url = 'https://www.mdpi.com/books/pdfview/book/' + bookno
                    eb.provider = 'MDPI Books'
                    eb.format =  'online'
                else:
                    eb.url = eb.url.split('?')[0]
                eb.active = False
                eb.save()
    
        
        
