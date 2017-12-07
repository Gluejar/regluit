from django.core.management.base import BaseCommand

from regluit.core.loaders.springer import load_springer

class Command(BaseCommand):
    help = "load books from springer open"
    args = "<pages>"


    def handle(self, pages, **options):
        books = load_springer(int(pages))        
        print "loaded {} books".format(len(books))
