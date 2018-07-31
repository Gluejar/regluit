# if there's an edition without a work, something went wrong.

from django.core.management.base import BaseCommand

from regluit.core import models

class Command(BaseCommand):
    help = "removes editions with no connected works"

    def handle(self,  **options):
        numeditions=0
        deleted=0
        for edition in models.Edition.objects.all():
            if not edition.work:
                edition.delete()
                deleted=deleted+1
            numeditions=numeditions+1
        self.stdout.write("%s deleted from %s total" % (deleted, numeditions))
