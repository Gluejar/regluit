"""
Load the Gutenberg editions

"""

from django.core.management.base import BaseCommand

from regluit.core import models
from regluit.test import booktests

class Command(BaseCommand):
    help = "load Gutenberg editions"
    args = "<max_num>"
    
    def handle(self, max_num, **options):

        try:
            max_num = int(max_num)
        except:
            max_num = None

        print "number of Gutenberg editions (before)", \
             models.Edition.objects.filter(identifiers__type='gtbg').count()        
        print "number of Gutenberg ebooks (before)", \
             models.Ebook.objects.filter(edition__identifiers__type='gtbg').count()
        
        booktests.load_gutenberg_books(max_num=max_num)
        
        print "number of Gutenberg editions (after)", \
             models.Edition.objects.filter(identifiers__type='gtbg').count()        
        print "number of Gutenberg ebooks (after)", \
             models.Ebook.objects.filter(edition__identifiers__type='gtbg').count()
   
