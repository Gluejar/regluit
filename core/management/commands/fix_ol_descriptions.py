
from django.core.management.base import BaseCommand
from regluit.core import models, bookloader

class Command(BaseCommand):
    help = "do OL relookup if description contains { "
    
    def handle(self, **options):
        print "Number of Works with { in description: %s" % models.Work.objects.filter(description__contains='{').count()
        
        for work in models.Work.objects.filter(description__contains='{'):
            print "updating work %s" % work 
            bookloader.add_openlibrary(work)           
