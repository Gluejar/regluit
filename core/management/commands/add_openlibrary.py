from django.core.management.base import BaseCommand

from regluit.core import models, bookloader

class Command(BaseCommand):

    def handle(self, *args, **options):
        for work in models.Work.objects.filter(openlibrary_lookup__isnull=True):
            self.stdout.write("loading openlibrary data for %s" % work)
            bookloader.add_openlibrary(work)
