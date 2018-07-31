from itertools import islice

from django.conf import settings
from django.core.management.base import BaseCommand

from regluit.core.goodreads import GoodreadsClient

class Command(BaseCommand):
    help = "list books on given user bookshelf"

    def add_arguments(self, parser):
        parser.add_argument('user_id', nargs='+', type="int", help="user_id")    
        parser.add_argument('shelf_name', nargs='+', help="shelf_name")    
        parser.add_argument('max_books', nargs='?', default=100, type="int", help="max_books")    
    
    def handle(self, user_id, shelf_name, max_books, **options):
        gc = GoodreadsClient(key=settings.GOODREADS_API_KEY, secret=settings.GOODREADS_API_SECRET)
        for (i, review) in enumerate(islice(gc.review_list(user_id, shelf=shelf_name), max_books)):
            self.stdout.write('{}, {}, {}, {}'.format( i, review["book"]["title"],
                review["book"]["isbn10"], review["book"]["small_image_url"]))