import re

from django.core.management.base import BaseCommand

from django.db.models import Sum

from regluit.core.models import Work, Ebook
from regluit.core.loaders.harvest import DOWNLOADABLE


class Command(BaseCommand):
    help = "fix inactive Ebooks"

    def handle(self, **options):

        qs = Work.objects.annotate(num_free=Sum('editions__ebook_files')).filter(num_free__gt=0)
        self.stdout.write(str(qs.filter(is_free=False).count()))
        for free in qs.filter(is_free=False):
            for ebook in Ebook.objects.filter(edition__work_id=free.id, format__in=DOWNLOADABLE).order_by('-created'):
                ebook.activate()
                break
        self.stdout.write(str(qs.filter(is_free=False).count()))

