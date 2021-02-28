import csv
import json
from django.core.management.base import BaseCommand

from regluit.core.models import Identifier

class Command(BaseCommand):
    help = "translate doab ids to handles"
    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='?', help="filename")    

    def handle(self, filename, **options):
        self.stdout.write("doab ids to start: %s" % Identifier.objects.filter(type='doab').count())
        with open(filename, 'r') as jsonfile:
            newdoab = json.loads(jsonfile.read())
        for doab in Identifier.objects.filter(type='doab'):
            if doab.value.startswith("20.500.12854"):
                continue
            if doab.value in newdoab:
                # already done
                if Identifier.objects.filter(type='doab', value=newdoab[doab.value]).exists():
                    doab.delete()
                else:
                    doab.value = newdoab[doab.value]
                    doab.save()
            else:
                doab.delete()
        self.stdout.write("doab ids at end: %s" % Identifier.objects.filter(type='doab').count())

