from django.core.management.base import BaseCommand

from regluit.core.models import Subject



class Command(BaseCommand):
    '''Have observed that if the subject has more than two commas in it, it probably means something else'''
    help = "delete subjects whose names have more than 2 commas"
    
    def handle(self, **options):
       comma_subjects = Subject.objects.filter(name__contains=",")

       for subject in comma_subjects:
            num_commas = len(subject.name.split(','))-1
            if num_commas >2:
                self.stdout.write(subject.name)
                subject.delete()
