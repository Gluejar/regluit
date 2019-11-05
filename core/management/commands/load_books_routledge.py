from django.core.management.base import BaseCommand

from regluit.core.loaders.routledge import load_routledge

class Command(BaseCommand):
    help = "load books from routledge"

    def handle(self, **options):        
        books = load_routledge()       
        self.stdout.write("loaded {} books".format(len(books)))
        
