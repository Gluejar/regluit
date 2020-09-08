import requests
from django.core.management.base import BaseCommand

from regluit.core.models import Ebook

class Command(BaseCommand):
    help = "check ebooks for 404s and remove if needed"
    args = "<limit>"

    def add_arguments(self, parser):
        parser.add_argument('limit', nargs='?', type=int, default=50, help="max to check")
        parser.add_argument('--ebook', nargs='?', type=int, default=0, help="ebook to check")
        parser.add_argument('--provider', nargs='?', type=str, default='', help="provider to check")
        parser.add_argument('--format', nargs='?', type=str, default='online', help="format to check")

    def handle(self, limit=0, **options):
        limit = int(limit) if limit else 0
        format = options.get('format')
        if format == 'all':
            onlines = Ebook.objects.all()
        else:
            onlines = Ebook.objects.filter(format=format)
        if options.get('ebook'):
            onlines = Ebook.objects.filter(id=options.get('ebook'))
        elif options.get('provider'):
            onlines = onlines.filter(provider=options.get('provider'))
        removed = []
        done = 0
        for online in onlines:
            if not online.ebook_files.exists():
                r = requests.get(online.url)
                if r.status_code == 404:
                    removed.append(online.edition.id)
                    self.stdout.write(online.edition.title)
                    online.delete()
                done +=1
            if done >= limit or done >= 500:
                break
        self.stdout.write("%s ebooks checked" % done)
        self.stdout.write("%s ebooks removed" % len(removed))
