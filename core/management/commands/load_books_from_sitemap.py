from django.core.management.base import BaseCommand

from regluit.core.bookloader import add_by_sitemap

class Command(BaseCommand):
    help = "load books based on a website sitemap"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('url')

        # Named (optional) arguments
        parser.add_argument(
            '--max',
            dest='max',
            type=int,
            default=None,
            nargs='?', 
            help='set a maximum number of books to load',
        )

    def handle(self, url, max=None, **options):
        books = add_by_sitemap(url, maxnum=max)        
        print "loaded {} books".format(len(books))
