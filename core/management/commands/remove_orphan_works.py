# no, not that kind of orphan works. removes works with no connected identifiers.

from django.core.management.base import BaseCommand

from regluit.core import models

class Command(BaseCommand):
    help = "removes works with no connected identifiers"

    def handle(self,  **options):
        numworks=0
        deleted=0
        for work in models.Work.objects.all():
            if work.identifiers.count()==0:
                work.delete()
                deleted=deleted+1
            numworks=numworks+1
        self.stdout.write("%s deleted from %s total" % (deleted, numworks))
