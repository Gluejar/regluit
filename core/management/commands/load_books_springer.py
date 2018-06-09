from django.core.management.base import BaseCommand

from regluit.core.loaders.springer import load_springer

class Command(BaseCommand):
    help = "load books from springer open"
    args = "<startpage> <endpage>"


    def handle(self, startpage, endpage=0, **options):        
        books = load_springer(int(startpage), int(endpage))       
        print "loaded {} books".format(len(books))
