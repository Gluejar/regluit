"""
a variety of errors can cause works to not get clustered by add_editions, or a new isbn can take time to get incorporated into clustering services.
The signature of both problems is a work with only one related edition, a singleton.
This script goes through all singleton works and attempts to add_related. 'xx' works are excluded from being source works
"""

from itertools import islice

from django.core.management.base import BaseCommand
from django.db.models import Count

from regluit.core import models, bookloader

class Command(BaseCommand):
    help = "add and merge editions for singleton works"
    args = "<language> <max> <start>"
    

    def handle(self, language, max=100, start=0, **options):
        print "Number of singleton Works with language = %s: %s" % (language, models.Work.objects.annotate(num_editions=Count('editions')).filter(num_editions=1, language=language).count())
        
        try:
            max = int(max)
        except:
            max = 100
        try:
            start = int(start)
        except:
            start = 0
        
        for (i, work) in enumerate(islice(models.Work.objects.annotate(num_editions=Count('editions')).filter(num_editions=1, language=language),start,start+max)):
            #check that there's still only one edition
            print "%d %s id:%s #editions:%d #isbn:%s -->" % (i, work.title.encode('ascii','ignore'), work.id,  work.editions.count(), work.first_isbn_13()),
            work_id=work.id
            if work.editions.count() != 1:
                print
                continue
            isbn=work.first_isbn_13()
            if isbn:
                new_work = bookloader.relate_isbn( isbn )
                if new_work is None:
                    print "failed to get edition"
                elif new_work.id != work_id:
                    print "added edition to work %s with %s editions" % (new_work.id, new_work.editions.count())
                else:
                    if work.editions.count()>1:
                        print "singleton joined to new edition" 
                    else:
                        print "singleton edition not moved" 
            else:
                print "no ISBN for this work and therefore no new editions"
        print "Updated Number of singleton Works with language = %s: %s" % (language,models.Work.objects.annotate(num_editions=Count('editions')).filter(num_editions=1, language=language).count() )
