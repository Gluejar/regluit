"""
a variety of errors can cause works to not get clustered by add_editions, or a new isbn can take time to get incorporated into clustering services.
The signature of both problems is a work with only one related edition, a singleton.
This script goes through all singleton works and attempts to add_related. 'xx' works are excluded from being source works
"""

from django.core.management.base import BaseCommand
from django.db.models import Count
from regluit.core import models, bookloader

class Command(BaseCommand):
    help = "add and merge editions for singleton works"
    args = "<language>"

    def handle(self, language, **options):
        print "Number of singleton Works with language = %s: %s" % (language, models.Work.objects.annotate(num_editions=Count('editions')).filter(num_editions=1, language=language).count())
        
        for work in models.Work.objects.annotate(num_editions=Count('editions')).filter(num_editions=1, language=language):
            #check that there's still only one edition
            if work.editions.count() != 1:
                continue
            new_editions = bookloader.add_related( work.first_isbn_13() )
            print "clustered %s editions for work %s" % (len(new_editions),work )
        print "Updated Number of singleton Works with language = %s: %s" % (language,models.Work.objects.annotate(num_editions=Count('editions')).filter(num_editions=1, language=language).count() )
