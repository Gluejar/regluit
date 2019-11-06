import re
from django.core.management.base import BaseCommand
from regluit.bisac.models import BisacHeading
from regluit.core.models import Subject
from regluit.core.loaders.utils import add_subject

bisac_pattern = re.compile(r'[A-Z]{3}\d+')

class Command(BaseCommand):
    help = "fix bisac headings"
    
    def handle(self, **options):
        for subject in Subject.objects.filter(name__contains='bisac'):
            print subject.name
            match = bisac_pattern.search(subject.name)
            bisac_code = match.group(0) if match else None
            if bisac_code:
                try:
                    bisac_heading = BisacHeading.objects.get(notation=bisac_code)
                    for work in subject.works.all():
                        while bisac_heading:
                            add_subject(bisac_heading.full_label, work, authority="bisacsh")
                            bisac_heading = bisac_heading.parent
                    subject.delete()
                except  BisacHeading.DoesNotExist:
                    self.stdout.write("no Bisac heading with notation %s" % bisac_code)
