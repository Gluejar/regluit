from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from regluit.core import bookloader

class Command(BaseCommand):
    help = "populate a user's wishlist with books from a file of isbns"
    args = "<filename> <username>"

    def handle(self, filename, username, **options):
        user = User.objects.get(username=username)
        wishlist = user.wishlist
        for isbn in open(filename):
            isbn = isbn.strip()
            edition = bookloader.add_by_isbn(isbn)
            bookloader.add_related(isbn)

            user.wishlist.add_work(edition.work, source="user")


            if edition:
                print "loaded %s as %s" % (isbn, edition)
            else:
                print "failed to load book for %s" % isbn
