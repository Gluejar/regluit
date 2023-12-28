from django.core.management.base import BaseCommand

from regluit.core.loaders.springer import load_springer, SpringerScraper
from regluit.core.bookloader import add_from_bookdatas

class Command(BaseCommand):
    help = "load books from springer open"

    def add_arguments(self, parser):
        parser.add_argument('startpage', nargs='?', type=int, default=1, help="page to start on")    
        parser.add_argument('endpage', nargs='?', type=int, default=1, help="page to end on")
        parser.add_argument('--url', nargs='?', default='', help="url to scrape")
      

    def handle(self, startpage, endpage=0, **options):        
        if options.get('url'):
            books = add_from_bookdatas([SpringerScraper(options.get('url'))])
        else:
            books = load_springer(int(startpage), int(endpage))       
        self.stdout.write("loaded {} books".format(len(books)))
        
        for edition in books:
            done_fmt = set()
            for ebook in edition.work.ebooks_all():
                for fmt in ['pdf', 'epub', 'mobi']:
                    if ebook.format == fmt:
                        if fmt not in done_fmt:
                            ebook.activate()
                            done_fmt.add(fmt)
                        else:
                            ebook.deactivate()

