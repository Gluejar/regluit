"""
a variety of errors can cause works to not get clustered by add_editions, or a new isbn can take time to get incorporated into clustering services.
The signature of both problems is a work with only one related edition, a singleton.
This script goes through all singleton works and attempts to add_related. 'xx' works are excluded from being source works
"""

from django.core.management.base import BaseCommand
from django.db.models import Count
from regluit.core import models, bookloader
from itertools import islice

class Command(BaseCommand):
    help = "add and merge editions for singleton works"
    args = "<language> <max>"
    

    def handle(self, language, max=100, **options):
        print "Number of singleton Works with language = %s: %s" % (language, models.Work.objects.annotate(num_editions=Count('editions')).filter(num_editions=1, language=language).count())
        
        try:
            max = int(max)
        except:
            max = None
        
        for (i, work) in enumerate(islice(models.Work.objects.annotate(num_editions=Count('editions')).filter(num_editions=1, language=language),max)):
            #check that there's still only one edition
            print "%d %s id:%s #editions:%d #isbn:%s -->" % (i, work.title.encode('ascii','ignore'), work.id,  work.editions.count(), work.first_isbn_13()),
            if work.editions.count() != 1:
                print
                continue
            isbn=work.first_isbn_13()
            if isbn:
                new_work = bookloader.relate_isbn( isbn )
                if new_work.id != work.id:
                    print "added edition to work %s with %s editions" % (new_work.id, new_work.editions.count())
                else:
                    print "%s editions not moved" % work.editions.count()
            else:
                print "no ISBN for this work and therefore no new editions"
        print "Updated Number of singleton Works with language = %s: %s" % (language,models.Work.objects.annotate(num_editions=Count('editions')).filter(num_editions=1, language=language).count() )
