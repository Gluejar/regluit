from django.core.management.base import BaseCommand

from regluit.core.loaders import doab

class Command(BaseCommand):
    help = "load doab books via oai"

    def add_arguments(self, parser):
        parser.add_argument('from_year', nargs='?', type=int, default=None, help="year to start on")    
        parser.add_argument('limit', nargs='?', type=int, default=None, help="desired records")    
    
    def handle(self, from_year= None, limit=None, **options):
        from_year = int(from_year) if from_year else None
        limit = int(limit) if limit else None
        if limit:
            doab.load_doab_oai(from_year=from_year, limit=limit)
        else:
            if from_year:
                doab.load_doab_oai(from_year=from_year)
            else:
                doab.load_doab_oai()
