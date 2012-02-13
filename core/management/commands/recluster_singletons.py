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
    

    def handle(self, language, max, **options):
        print "Number of singleton Works with language = %s: %s" % (language, models.Work.objects.annotate(num_editions=Count('editions')).filter(num_editions=1, language=language).count())
        
        try:
            max = int(max)
        except:
            max = None
        
        for (i, work) in enumerate(islice(models.Work.objects.annotate(num_editions=Count('editions')).filter(num_editions=1, language=language),max)):
            #check that there's still only one edition
            print "%d %s id:%s #editions:%d #isbn:%s -->" % (i, work.encode('ascii','ignore'), work.id,  work.editions.count(), work.first_isbn_13()),
            if work.editions.count() != 1:
                print
                continue
            if work.first_isbn_13():
                new_editions = bookloader.add_related( work.first_isbn_13() )
                corresponding_works =  set([ed.work for ed in new_editions])
                print "clustered %s editions for work %s" % (len(new_editions),work ), \
                      "| Corresponding works : ", [(w.id, w.language, w.editions.count()) for w in corresponding_works], \
                      "#corresponding_works:%s" % (len(corresponding_works))
            else:
                print "no ISBN for this work and therefore no new editions"
        print "Updated Number of singleton Works with language = %s: %s" % (language,models.Work.objects.annotate(num_editions=Count('editions')).filter(num_editions=1, language=language).count() )
