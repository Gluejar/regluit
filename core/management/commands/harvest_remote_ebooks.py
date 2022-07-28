from random import shuffle
from django.core.management.base import BaseCommand

from regluit.core.loaders.harvest import archive_dl, RateLimiter, DONT_HARVEST
from regluit.core.models import Ebook
from regluit.core.parameters import GOOD_PROVIDERS
DOWNLOADABLE = ['pdf', 'epub']

DONT_CHECK = list(GOOD_PROVIDERS) + DONT_HARVEST

class Command(BaseCommand):
    help = "check/harvest ebooks from 'remote' ebooks"
    args = "<limit>"

    def add_arguments(self, parser):
        parser.add_argument('limit', nargs='?', type=int, default=0, help="max to harvest")
        parser.add_argument('--ebook', nargs='?', type=int, default=0, help="ebook to harvest")
        parser.add_argument('--provider', nargs='?', default='', help="provider to harvest")
        parser.add_argument('--format', nargs='?', default='all', help="format to harvest")
        parser.add_argument('--trace', action='store_true', help="trace")

    def handle(self, limit=0, trace=False, **options):
        limit = int(limit) if limit else 0
        rl = RateLimiter()
        format = options.get('format')
        if format == 'all':
            onlines = Ebook.objects.filter(format__in=DOWNLOADABLE)
        else:
            onlines = Ebook.objects.filter(format=format)
        if options.get('ebook'):
            onlines = Ebook.objects.filter(id=options.get('ebook'))
        elif options.get('provider'):
            onlines = onlines.filter(provider=options.get('provider'))
        else:
            onlines = onlines.exclude(provider__in=DONT_CHECK)
            online_ids = [ebook.id for ebook in onlines]
            self.stdout.write('%s ebooks need checking.' % len(onlines))
            shuffle(online_ids)
            onlines = (Ebook.objects.get(id=id) for id in online_ids)
        archived = {}
        failed = {}
        done = 0
        for online in onlines:
            if trace:
                self.stdout.write(str(online.id))
            status = archive_dl(online, limiter=rl.delay)
            if status ==  1:
                done += 1
                archived[online.provider] = archived.get(online.provider, 0) + 1
                self.stdout.write(online.edition.title)
            elif status == -1:
                done += 1
                failed[online.provider] = failed.get(online.provider, 0) + 1
                online.format = 'online'
                online.active = False
                online.save()
            if done >= limit or done >= 2000:
                break
        self.stdout.write("archived")
        for result in [archived, failed]:
            for provider in result:
                self.stdout.write('%s\t%s' % (provider, result[provider]))
            self.stdout.write("failed")
