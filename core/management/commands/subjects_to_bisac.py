import string
from django.core.management.base import BaseCommand
from regluit.bisac.models import BisacHeading
from regluit.core.models import Subject

class Command(BaseCommand):
    help = "add and convert existing subjects to Bisac"
    
    def handle(self, **options):
        matches=0
        for bisac_heading in BisacHeading.objects.all():
            for subject in Subject.objects.filter(name=bisac_heading.full_label):
                subject.authority='bisacsh'
                subject.name = bisac_heading.full_label
                subject.save()
                matches += 1
        self.stdout.write("%s bisac headings converted" % matches)
