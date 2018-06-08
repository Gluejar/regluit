from django.core.management.base import BaseCommand
from regluit.core.models import Work


class Command(BaseCommand):
    help = "generate mobi ebooks where needed and possible."
    args = "<max>"
    
    def handle(self, max=None, **options):
        if max:
            try:
                max = int(max)
            except ValueError:
                max = 1
        else:
            max = 1
        epubs = Work.objects.filter(editions__ebooks__format='epub').distinct().order_by('-id')

        i = 0
        for work in epubs:
            if not work.ebooks().filter(format="mobi"):
                for ebook in work.ebooks().filter(format="epub"):
                    ebf = ebook.get_archive_ebf()
                    if ebf and ebf.mobied >= 0:
                        try:
                            print u'making mobi for {}'.format(work.title)
                            if ebf.make_mobi():
                                print 'made mobi'
                                i = i + 1
                                break
                            else:
                                print 'failed to make mobi'
                        except:
                            print 'failed to make mobi'
            if i >= max:
                break
