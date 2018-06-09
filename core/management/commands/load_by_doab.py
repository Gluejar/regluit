from django.core.management.base import BaseCommand

from regluit.core.loaders import doab

class Command(BaseCommand):
    help = "load doab books by doab_id via oai"
    args = "<doab_id>"
    
    def handle(self, doab_id, **options):
        doab.add_by_doab(doab_id)
