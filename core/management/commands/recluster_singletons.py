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
    def add_arguments(self, parser):
        parser.add_argument('language', nargs='+', help="language code")    
        parser.add_argument('max', nargs='?', type='int', default=100, help="max singletons to process")    
        parser.add_argument('start', nargs='?', type='int', default=0, help="start")    
    

    def handle(self, language, max=100, start=0, **options):
        self.stdout.write("Number of singleton Works with language = %s: %s" % (
            language,
            models.Work.objects.annotate(
                num_editions=Count('editions')).filter(num_editions=1, language=language).count()
            )
        )
        
        for (i, work) in enumerate(islice(
            models.Work.objects.annotate(
                num_editions=Count('editions')).filter(num_editions=1, language=language),
                start,
                start + max
            )
        ):
            #check that there's still only one edition
            self.stdout.write("%d %s id:%s #editions:%d #isbn:%s -->" % (
                i,
                work.title.encode('ascii','ignore'),
                work.id,
                work.editions.count(),
                work.first_isbn_13(),
            )
            work_id = work.id
            if work.editions.count() != 1:
                self.stdout.write()
                continue
            isbn=work.first_isbn_13()
            if isbn:
                new_work = bookloader.relate_isbn( isbn )
                if new_work is None:
                    self.stdout.write("failed to get edition")
                elif new_work.id != work_id:
                    self.stdout.write("added edition to work %s with %s editions" % (new_work.id, new_work.editions.count()))
                else:
                    if work.editions.count()>1:
                        self.stdout.write("singleton joined to new edition")
                    else:
                        self.stdout.write("singleton edition not moved")
            else:
                self.stdout.write("no ISBN for this work and therefore no new editions")
        self.stdout.write("Updated Number of singleton Works with language = %s: %s" % (
            language,
            models.Work.objects.annotate(
                num_editions=Count('editions')).filter(num_editions=1,language=language).count()
            )
        )
