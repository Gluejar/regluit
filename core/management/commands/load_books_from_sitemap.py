import os
from django.core.management.base import BaseCommand

from regluit.core.loaders import add_by_sitemap

class Command(BaseCommand):
    help = "load books based on a website sitemap; use url=all to load from sitemap list"

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
        if url == 'all':
            file_name = "../../../bookdata/sitemaps.txt"
            command_dir =  os.path.dirname(os.path.realpath(__file__))
            file_path = os.path.join(command_dir, file_name)
            with open(file_path) as f:
                content = f.readlines()
            books = []
            for sitemap in content:
                added = add_by_sitemap(sitemap.strip(), maxnum=max)
                max = max - len(added) if max else max
                books =  books + added
                if max and max < 0:
                    break
        else:
            books = add_by_sitemap(url, maxnum=max)  
              
        self.stdout.write("loaded {} books".format(len(books)))
