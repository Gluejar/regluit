from django.core.management.base import BaseCommand
from regluit.marc.models import import_records

class Command(BaseCommand):
    help = "load records from a file "
    args = "<file>"
    
    def handle(self, file, **options):
        xml_file = open(file,'r')
        num_loaded = import_records(xml_file)
        print '%s records created' % num_loaded
