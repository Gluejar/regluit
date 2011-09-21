from django.core.management.base import BaseCommand

from regluit.core import models

class Command(BaseCommand):
    help = "list all editions in the database"

    def handle(self, *args, **options):
        editions = models.Edition.objects.all()
        for edition in editions:
            print edition.id, edition.title, edition.isbn_10, edition.isbn_13
