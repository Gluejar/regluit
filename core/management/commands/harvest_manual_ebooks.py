from random import shuffle
from django.core.management.base import BaseCommand

from regluit.core.loaders.harvest import harvest_manual
from regluit.core.models import Ebook

class Command(BaseCommand):
    help = "load manually harvested ebooks"

    def add_arguments(self, parser):
        parser.add_argument('--ebook', nargs='?', type=int, default=0, help="ebook to harvest")
        parser.add_argument('--provider', nargs='?', default='', help="provider to harvest")

    def handle(self, limit=0, trace=False, **options):
        if options.get('ebook'):
            onlines = Ebook.objects.filter(id=options.get('ebook'))
        elif options.get('provider'):
            onlines = Ebook.objects.filter(provider=options.get('provider'))
            self.stdout.write('%s onlines to check' % onlines.count())
        done = 0
        providers = {}
        
        for online in onlines:
            new_ebf, new = harvest_manual(online)
            if new_ebf and new:
                done += new
                providers[online.provider] = providers.get(online.provider, 0) + 1
                self.stdout.write(new_ebf.edition.work.title)
        self.stdout.write('harvested {} ebooks'.format(done))
        self.stdout.write(str(providers))
