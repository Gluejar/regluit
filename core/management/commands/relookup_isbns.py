"""
To avoid continually hitting google, a failed isbn lookup from add_related creates a work and on edition with language = "xx"
this command goes through all these editions and checks them in google books
"""

from django.core.management.base import BaseCommand
from regluit.core import models, bookloader

class Command(BaseCommand):
    help = "relookup all editions attached to language=xx works"
    def add_arguments(self, parser):
        parser.add_argument('title', nargs='?', default='', help="start of title")    
    
    def handle(self, title='', **options):
        self.stdout.write("Number of Works with language=xx, title like %s: %s" % (title, models.Work.objects.filter(language='xx', title__istartswith=title).count()))
        updated_num = 0
        
        for work in models.Work.objects.filter(language='xx', title__istartswith=title):
            self.stdout.write("updating work %s" % work)          
            for edition in work.editions.all():
                self.stdout.write("updating edition %s" % edition)
                updated = bookloader.update_edition(edition)
                if updated.work.language!= 'xx':
                    updated_num+=1
        self.stdout.write("Number of updated editions= %s" % updated_num)
