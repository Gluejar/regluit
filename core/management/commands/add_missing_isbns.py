from django.core.management.base import BaseCommand
from regluit.core import bookloader 

class Command(BaseCommand):
    help = "Add ISBNs missing from Editions"
    args = "<max_num> <confirm>"
    
    def handle(self, max_num=None, confirm=True, **options):
        if max_num == 'None':
            max_num = None
        else:
            try:
                max_num = int(max_num)
            except:
                max_num = None
        results = bookloader.add_missing_isbn_to_editions(max_num=max_num, confirm=confirm)
        print results
        
