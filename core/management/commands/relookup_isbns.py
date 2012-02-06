"""
To avoid continually hitting google, a failed isbn lookup from add_related creates a work and on edition with language = "xx"
this command goes through all these editions and checks them in google books
"""

from django.core.management.base import BaseCommand
from regluit.core import models, bookloader

class Command(BaseCommand):
    help = "relookup all editions attached to language=xx works"
    
    def handle(self, **options):
        print "Number of Works with language=xx: %s" % models.Work.objects.filter(language='xx').count()
        updated_num=0
        
        for work in models.Work.objects.filter(language='xx'):
            print "updating work %s" % work            
            for edition in work.editions.all():
                print "updating edition %s" % edition
                updated = bookloader.update_edition(edition)
                if updated.work.language!= 'xx':
                    updated_num+=1
        print "Number of updated editions= %s" % updated_num
