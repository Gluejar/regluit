from django.core.management.base import BaseCommand

from regluit.core.loaders.doab_utils import online_to_download
from regluit.core.models import Ebook
from regluit.core.loaders.utils import type_for_url

class Command(BaseCommand):
    help = "fix 'online' ebooks"
    args = "<limit>"

    def add_arguments(self, parser):
        parser.add_argument('limit', nargs='?', type=int, default=0, help="max to harvest")

    def handle(self, limit=0, **options):
        limit = int(limit) if limit else 0
        onlines = Ebook.objects.filter(format='online', provider='SciELO')
        done = 0
        for online in onlines:
            urls = online_to_download(online.url)
            for url in urls:
                online.format = type_for_url(url, force=True)
                online.active = True
                online.save()
                done += 1
                self.stdout.write(unicode(online.edition.work.title))
            if done > limit:
                break
        self.stdout.write('fixed {} ebooks'.format(done))
        if done == 100:
            self.stdout.write('100 is the maximum; repeat to do more')
