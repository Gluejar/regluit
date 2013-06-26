from itertools import islice

from django.conf import settings
from django.core.management.base import BaseCommand

from regluit.core.goodreads import GoodreadsClient

class Command(BaseCommand):
    help = "list books on given user bookshelf"
    args = "<user_id shelf_name max_books>"
    
    def handle(self, user_id, shelf_name, max_books, **options):
        max_books = int(max_books)
        gc = GoodreadsClient(key=settings.GOODREADS_API_KEY, secret=settings.GOODREADS_API_SECRET)
        for (i, review) in enumerate(islice(gc.review_list(user_id,shelf=shelf_name),max_books)):
            print i, review["book"]["title"], review["book"]["isbn10"], review["book"]["small_image_url"]