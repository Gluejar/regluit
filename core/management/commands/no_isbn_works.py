"""
list works with no isbn
"""

from django.core.management.base import BaseCommand
from django.db.models import Count
from regluit.core import models

class Command(BaseCommand):
    help = "list works with no isbn. actions: count, list, wished"
    args = "<action>"

    
    def handle(self, action='count', **options):
        no_isbn_works=models.Work.objects.exclude(identifiers__type='isbn')
        num=no_isbn_works.count()
        print "%s works without isbn:"% num
        if action=='list':
            for  work in no_isbn_works:
                print "%s, %s"% (work.id, work.title)
        elif action=='wished':
            print "%s wished works without isbn:"% no_isbn_works.filter(num_wishes__gt=0).count()
            for  work in no_isbn_works.filter(num_wishes__gt=0):
                print "%s, %s, %s"% (work.id, work.title, work.num_wishes)
            
            
