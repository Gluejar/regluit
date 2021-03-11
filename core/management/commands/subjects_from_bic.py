import string
from django.core.management.base import BaseCommand
from regluit.core.models import Subject
from regluit.core.validation import explode_bic

class Command(BaseCommand):
    help = "explode compound bic subjects from doab"
    
    def handle(self, **options):
        matches=0
        for subject in Subject.objects.filter(name__startswith='bic Book Indus'):
            newsubs = explode_bic(subject.name)
            for work in subject.works.all():
                for subsub in newsubs:
                    Subject.set_by_name(subsub, work)
            subject.delete()
            
        self.stdout.write("bic headings exploded" )
