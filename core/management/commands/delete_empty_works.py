from django.core.management.base import BaseCommand

from regluit.core.models import Work



class Command(BaseCommand):
    '''remove works and editions without titles'''
    help = "remove works and editions without titles"
    
    def handle(self, **options):
       badworks = Work.objects.filter(title='')

       for work in badworks:
            work.selected_edition = None
            for edition in work.editions.all():
                edition.delete()
            work.delete()
