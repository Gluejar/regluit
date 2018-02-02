from __future__ import print_function

from django.core.management.base import BaseCommand
from django.db import IntegrityError

from regluit.core import models

class Command(BaseCommand):
    help = "clean work and edition titles, work descriptions, and author and publisher names"
    
    def handle(self, **options):
        for ident in models.Identifier.objects.filter(type='http', edition__isnull=False):
            ident.edition = None
            ident.save()
        for edition in models.Edition.objects.filter(work__isnull=True):
            for ident in edition.identifiers.all():
                if ident.work:
                    edition.work = work
                    edition.save()
                    break
            if not edition.work:
                edition.delete()