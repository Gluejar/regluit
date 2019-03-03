from django.core.management.base import BaseCommand

from django.db.models import Count
from regluit.core.models import Work, Ebook, EbookFile

class Command(BaseCommand):
    help = "remove old online ebooks from same provider"
    
    def handle(self, **options):
        allonlines = Work.objects.filter(editions__ebooks__format='online').distinct()
        self.stdout.write('%s works with online ebooks' % allonlines.count())
        removed = 0
        for work in allonlines:
            onlines = Ebook.objects.filter(
                edition__work__id=work.id,
                format='online'
            ).order_by('-created')
            num_onlines = onlines.count()
            if num_onlines >= 2:
                new_provider = onlines[0].provider
                for online in onlines[1:]:
                    harvested = EbookFile.objects.filter(source=online.url).count()
                    if not harvested and online.provider == new_provider:
                        self.stdout.write(online.edition.work.title)
                        online.delete()
                        removed += 1
        self.stdout.write('%s online ebooks removed' % removed)