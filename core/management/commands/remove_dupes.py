from django.db.models import Count
from django.core.management.base import BaseCommand

from regluit.core import models

class Command(BaseCommand):
    help = "remove duplicates"

    def handle(self, *args, **options):
        q = models.Edition.objects.values("googlebooks_id")
        q = q.annotate(Count("googlebooks_id"))
        for r in q:
            if r['googlebooks_id__count'] == 1:
                continue
            print r['googlebooks_id']

