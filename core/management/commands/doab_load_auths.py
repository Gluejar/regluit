import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from regluit.core.loaders import doab

class Command(BaseCommand):
    help = "load doab auths"
    args = "<limit> <file_name>"
    
    def handle(self, limit=None, file_name="../../../bookdata/doab_auths.json", **options):

        command_dir =  os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(command_dir, file_name)
        doab.load_doab_auths(file_path, limit=int(limit) if limit else None)