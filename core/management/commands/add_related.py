from django.core.management.base import BaseCommand

from regluit.core import tasks, models

class Command(BaseCommand):
    help = "queues add related books for works that have only one edition"

    def handle(self, **options):
        for work in models.Work.objects.all():
            if work.editions.all().count() == 1:
                sole_edition = work.editions.all()[0]
                tasks.add_related.delay(sole_edition.isbn_10)

