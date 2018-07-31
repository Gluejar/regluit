from django.core.management.base import BaseCommand
from regluit.core.models import Work, EbookFile


class Command(BaseCommand):
    help = "generate mobi ebooks where needed and possible."

    def add_arguments(self, parser):
        parser.add_argument('max', nargs='?', type=int, default=1, help="maximum mobis to make")    
        parser.add_argument('--reset', '-r', action='store_true', help="reset failed mobi conversions")    
        
        
    def handle(self, max=None, **options):
        maxbad = 10
        if options['reset']:
            bads = EbookFile.objects.filter(mobied__lt=0)
            for bad in bads:
                bad.mobied = 0
                bad.save()
        
        epubs = Work.objects.filter(editions__ebooks__format='epub').distinct().order_by('-id')

        i = 0
        n_bad = 0
        for work in epubs:
            if not work.ebooks().filter(format="mobi"):
                for ebook in work.ebooks().filter(format="epub"):
                    ebf = ebook.get_archive_ebf()
                    if ebf and ebf.mobied >= 0:
                        try:
                            self.stdout.write(u'making mobi for {}'.format(work.title))
                            if ebf.make_mobi():
                                self.stdout.write('made mobi')
                                i += 1
                                break
                            else:
                                self.stdout.write('failed to make mobi')
                                n_bad += 1
                                
                        except:
                            self.stdout.write('failed to make mobi')
                            n_bad += 1
            if i >= max or n_bad >= maxbad:
                break
