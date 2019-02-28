from django.core.management.base import BaseCommand

from regluit.core.loaders.harvest import dl_online, RateLimiter
from regluit.core.models import Ebook

class Command(BaseCommand):
    help = "harvest downloadable ebooks from 'online' ebooks"
    args = "<limit>"

    def add_arguments(self, parser):
        parser.add_argument('limit', nargs='?', type=int, default=0, help="max to harvest")

    def handle(self, limit=0, **options):
        limit = int(limit) if limit else 0
        rl = RateLimiter()
        onlines = Ebook.objects.filter(format='online')
        done = 0
        for online in onlines:
            new_ebf, new = dl_online(online, limiter=rl.delay)
            if new_ebf and new:
                done += 1
                if done == limit or done == 50:
                    break
        self.stdout.write('harvested {} ebooks'.format(done))
        if done == 50:
            self.stdout.write('50 is the maximum; repeat to do more')
