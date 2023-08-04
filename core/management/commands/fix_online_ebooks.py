from django.core.management.base import BaseCommand

from regluit.core.loaders.doab_utils import online_to_download
from regluit.core.models import Ebook

class Command(BaseCommand):
    help = "deactivate dead oapen ebooks"
    args = "<limit>"

    def add_arguments(self, parser):
        parser.add_argument('limit', nargs='?', type=int, default=0, help="max to fix")

    def handle(self, limit=0, **options):
        limit = int(limit) if limit else 0
        onlines = Ebook.objects.filter(active=1, provider='OAPEN Library',
            url__contains='/download/')
        done = 0
        for online in onlines:
            online.active = False
            online.save()
            done += 1
            #self.stdout.write(online.edition.work.title)
            if done > limit:
                break
        self.stdout.write('fixed {} ebooks'.format(done))
        if done >= 1000:
            self.stdout.write('1000 is the maximum; repeat to do more')
