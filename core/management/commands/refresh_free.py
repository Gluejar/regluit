from django.core.management.base import BaseCommand
from django.db.models import Sum

from regluit.core.models import Work



class Command(BaseCommand):
    '''remove works and editions without titles'''
    help = "remove works and editions without titles"
    
    def handle(self, **options):
        qs = Work.objects.annotate(num_free=Sum('editions__ebooks__active')).filter(num_free__gt=0)
        for free in qs.filter(is_free=False):
            self.stdout.write('freeing %s' % free.title)
            free.is_free = True
            free.save()
