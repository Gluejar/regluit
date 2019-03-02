from django.core.management.base import BaseCommand
from django.db.models import Q

from regluit.core.loaders.harvest import dl_online, RateLimiter
from regluit.core.models import Ebook
from regluit.core.loaders.doab_utils import url_to_provider

class Command(BaseCommand):
    help = "recalculate provider from url"
    args = "<limit>"

    def add_arguments(self, parser):
        parser.add_argument('limit', nargs='?', type=int, default=0, help="max to harvest")

    def handle(self, limit=0, **options):
        done = 0
        limit = int(limit) if limit else 0
        unstripped = Ebook.objects.filter(Q(provider='') | Q(provider__startswith='www.'))
        for ebook in unstripped:
            ebook.url = ebook.url.strip()
            new_provider = url_to_provider(ebook.url)
            if new_provider != ebook.provider:
                ebook.provider = new_provider
                ebook.save()
                done += 1
        self.stdout.write('{} urls or netloc stripped'.format(done))
        done = 0
        stale = Ebook.objects.filter(Q(provider__icontains='doi') | Q(provider='Handle Proxy'))
        self.stdout.write('{} providers to update'.format(stale.count()))
        for ebook in stale:
            new_provider = url_to_provider(ebook.url)
            if new_provider != ebook.provider:
                ebook.provider = new_provider
                ebook.save()
                done += 1
                if done > limit or done >= 100:
                    break
        self.stdout.write('{} ebooks updated'.format(done))
        if done == 100:
            self.stdout.write('50 is the maximum; repeat to do more')
