from django.core.management.base import BaseCommand
from regluit.core import models

class Command(BaseCommand):
    help = "Do a few integrity checks on Works, Editions, and Identifiers"
    
    def handle(self, **options):
        print "Number of Works without identifiers:", models.Work.objects.filter(identifiers__isnull=True).count()