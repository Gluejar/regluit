from random import shuffle
from django.core.management.base import BaseCommand

from regluit.core.loaders.harvest import dl_online, RateLimiter
from regluit.core.models import Ebook

class Command(BaseCommand):
    help = "harvest downloadable ebooks from 'online' ebooks"
    args = "<limit>"

    def add_arguments(self, parser):
        parser.add_argument('limit', nargs='?', type=int, default=0, help="max to harvest")
        parser.add_argument('--ebook', nargs='?', type=int, default=0, help="ebook to harvest")
        parser.add_argument('--provider', nargs='?', default='', help="provider to harvest")
        parser.add_argument('--format', nargs='?', default='online', help="format to harvest")

    def handle(self, limit=0, **options):
        limit = int(limit) if limit else 0
        rl = RateLimiter()
        format = options.get('format')
        if options.get('ebook'):
            onlines = Ebook.objects.filter(id=options.get('ebook'))
        elif options.get('provider'):
            onlines = Ebook.objects.filter(provider=options.get('provider'), format=format)
        else:
            online_ids = [ebook.id for ebook in Ebook.objects.filter(format=format)]
            shuffle(online_ids)
            onlines = (Ebook.objects.get(id=id) for id in online_ids)
        done = 0
        for online in onlines:
            new_ebf, new = dl_online(online, limiter=rl.delay, format=format)
            if new_ebf and new:
                done += new
                self.stdout.write(new_ebf.edition.work.title)
                if done >= limit or done >= 500:
                    break
        self.stdout.write('harvested {} ebooks'.format(done))
        if done >= 500:
            self.stdout.write('500 is the maximum; repeat to do more')
