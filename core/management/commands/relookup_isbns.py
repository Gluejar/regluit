"""
To avoid continually hitting google, a failed isbn lookup from add_related creates a work and on edition with language = "xx"
this command goes through all these editions and checks them in google books
"""

from django.core.management.base import BaseCommand
from regluit.core import models, bookloader

class Command(BaseCommand):
    help = "relookup all editions attached to language=xx works"
    args = "<title>"
    
    def handle(self, title='', **options):
        print "Number of Works with language=xx, title like %s: %s" % (title, models.Work.objects.filter(language='xx', title__istartswith=title).count())
        updated_num=0
        
        for work in models.Work.objects.filter(language='xx', title__istartswith=title):
            print "updating work %s" % work            
            for edition in work.editions.all():
                print "updating edition %s" % edition
                updated = bookloader.update_edition(edition)
                if updated.work.language!= 'xx':
                    updated_num+=1
        print "Number of updated editions= %s" % updated_num
