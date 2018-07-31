from django.core.management.base import BaseCommand
from django.db.models import Q, F

from regluit.core import models

class Command(BaseCommand):
    help = "Do a few integrity checks on Works, Editions, and Identifiers"
    
    def handle(self, **options):
        self.stdout.write("Number of Works without identifiers: {}".format(
            models.Work.objects.filter(identifiers__isnull=True).count()))
        self.stdout.write("Last 20 Works without identifiers: ")
        for w in models.Work.objects.filter(identifiers__isnull=True).order_by('-created')[0:20]:
            self.stdout.write("id: %d | title: %s  | created: %s" % (w.id, w.title, w.created))

        # models.Work.objects.filter(identifiers__isnull=True).filter(editions__isnull=False)[0].identifiers.all()       
        self.stdout.write("Number of editions that are currently tied to Works w/o identifiers {}".format( 
            models.Edition.objects.filter(work__identifiers__isnull=True).count()))
        self.stdout.write("Number of Identifiers not tied to Works (should be 0): {}".format(  
            models.Identifier.objects.filter(work__isnull=True).count()))
        self.stdout.write("Number of Editions not tied to a Work (should be 0): {}".format(
            models.Edition.objects.filter(work__isnull=True).count()))
        self.stdout.write("Number of Ebooks not tied to an Edition (should be 0): {}".format(
            models.Ebook.objects.filter(edition__isnull=True).count()))
        
        # is the possibility of problems coming from the fact that there are two places to tie
        # Work and Edition -- 1) foreign key Edition.work = models.ForeignKey("Work", related_name="editions", null=True)
        #                     2) sharing the same Identifier.
        # check both that iff a pair of Work and Edition share an identifier, that Work and Edition have a foreign key relationship
        self.stdout.write("Number of Works that have editions->identifiers that don't lead back to the same work (should be 0): {}".format(
            models.Work.objects.filter(~Q(editions__identifiers__work__id = F('id'))).count()))
        # check that for all Identifier pairs with an Edition that Edition<->Work foreign key relationships ties the same Edition/Work
        self.stdout.write("Number of Identifier pairs with an Edition in which Edition<->Work foreign key relationships does not tie the same Edition/Work (should be 0): {}".format(
           models.Identifier.objects.filter(edition__isnull=False).filter(~Q(edition__work__id = F('work__id'))).count()))