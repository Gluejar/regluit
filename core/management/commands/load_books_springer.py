from django.core.management.base import BaseCommand

from regluit.core.loaders.springer import load_springer

class Command(BaseCommand):
    help = "load books from springer open"

    def add_arguments(self, parser):
        parser.add_argument('startpage', nargs='?', type=int, default=1, help="page to start on")    
        parser.add_argument('endpage', nargs='?', type=int, default=1, help="page to end on")    
   

    def handle(self, startpage, endpage=0, **options):        
        books = load_springer(int(startpage), int(endpage))       
        self.stdout.write("loaded {} books".format(len(books)))
