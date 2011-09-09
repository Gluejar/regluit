from django.core.management.base import BaseCommand

from regluit.core import books

class Command(BaseCommand):
    help = "load books based on a text file of ISBNs"
    args = "<filename>"

    def handle(self, filename, **options):
        for isbn in open(filename):
            isbn = isbn.strip()
            edition = books.add_book(isbn)
            if edition:
                print edition
            else:
                print "failed to load book for %s" % isbn
