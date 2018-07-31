import csv
from django.core.management.base import BaseCommand

from regluit.core.loaders.utils import UnicodeDictReader, load_from_books

class Command(BaseCommand):
    help = "load books based on a csv spreadsheet of onix data"
    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='+',  help="filename")    

    def handle(self, filename, **options):
        sheetreader= UnicodeDictReader(open(filename,'rU'), dialect=csv.excel_tab)
        load_from_books(sheetreader)        
        pself.stdout.write("finished loading")
