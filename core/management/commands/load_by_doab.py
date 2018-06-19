from django.core.management.base import BaseCommand

from regluit.core.loaders import doab

class Command(BaseCommand):
    help = "load doab books by doab_id via oai"

    def add_arguments(self, parser):
        parser.add_argument('doab_ids', nargs='+', type=int, default=1, help="doab ids to add")    
    
    def handle(self, doab_ids, **options):
        for doab_id in doab_ids:
            doab.add_by_doab(doab_id)
