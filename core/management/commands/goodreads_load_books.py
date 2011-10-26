from django.core.management.base import BaseCommand
from regluit.core.goodreads import GoodreadsClient
from regluit.core import tasks, bookloader
from django.conf import settings
from django.contrib.auth.models import User
from itertools import islice

class Command(BaseCommand):
    help = "list books on given user bookshelf"
    args = "<user_name goodreads_user_id shelf_name max_books>"
    
    def handle(self, user_name, goodreads_user_id, shelf_name, max_books, **options):
        
        user = User.objects.get(username=user_name)
        max_books = int(max_books)
        gc = GoodreadsClient(key=settings.GOODREADS_API_KEY, secret=settings.GOODREADS_API_SECRET)
        
        for (i, review) in enumerate(islice(gc.review_list(goodreads_user_id,shelf=shelf_name),max_books)):
            isbn = review["book"]["isbn10"] if review["book"]["isbn10"] is not None else review["book"]["isbn13"]
            print i, review["book"]["title"], isbn, review["book"]["small_image_url"]
            try:
                edition = bookloader.add_by_isbn(isbn)
                # add related editions asynchronously
                tasks.add_related.delay(isbn)
                user.wishlist.works.add(edition.work)
            except Exception, e:
                print "error adding ISBN %s: %s" % (isbn, e)