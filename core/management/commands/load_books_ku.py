from django.core.management.base import BaseCommand

from regluit.core.loaders.ku import load_ku

class Command(BaseCommand):
    help = "load books from knowledge unlatched"

    def add_arguments(self, parser):
        parser.add_argument('round', nargs='?', type=int, default=None, help="round to load")    
   

    def handle(self, round, **options):        
        books = load_ku(round)       
        self.stdout.write("loaded {} books".format(len(books)))
