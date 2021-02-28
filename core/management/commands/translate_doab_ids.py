import csv
from django.core.management.base import BaseCommand

from regluit.core.models import Identifier

class Command(BaseCommand):
    help = "translate doab ids to handles"
    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='+', help="filename")    

    def handle(self, filename, **options):
        with open(filename,'r') as jsonfile:
            newdoab = json.loads(jsonfile.read())
        for doab in Identifier.objects.filter(type='doab'):
            if doab.value in newdoab:
                doab.value = newdoab[doab.value]
                doab.save()
            else:
                doab.delete()
        self.stdout.write("new doab ids loaded!")

