from django.core.management.base import BaseCommand
from django.db.models import Count

from regluit.core.models import Work, WasWork
from regluit.core.bookloader import merge_works



class Command(BaseCommand):
    '''remove works and editions without titles'''
    help = "remove works and editions without titles"
    
    def handle(self, **options):
        orphans = Work.objects.annotate(num_editions=Count('editions')).filter(num_editions=0)
        for work in orphans:
            self.stdout.write('cleaning %s' % work.title)
            parent = None
            for parent in WasWork.objects.filter(was=work.id):
                # remerge into parent
                merge_works(parent.work, work)
            if not parent:
                work.delete()
