import string
from django.core.management.base import BaseCommand
from regluit.bisac.models import populate_bisac_headings,attach_dangling_branches


class Command(BaseCommand):
    help = "build the bisac heading db"
    
    def handle(self, **options):
        populate_bisac_headings()
        attach_dangling_branches()
        print "bisac table is ready"
