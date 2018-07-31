from django.core.management.base import BaseCommand

from regluit.core import models, bookloader

class Command(BaseCommand):
    help = "do OL relookup if description contains { "
    
    def handle(self, **options):
        self.stdout.write("Number of Works with { in description: %s" % models.Work.objects.filter(description__contains='{').count())
        
        for work in models.Work.objects.filter(description__contains='{'):
            self.stdout.write("updating work %s" % work)
            bookloader.add_openlibrary(work, hard_refresh = True)           
