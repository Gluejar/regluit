from django.core.management.base import BaseCommand

from regluit.core.models import Subject
from regluit.core.validation import valid_subject



class Command(BaseCommand):
    '''Have observed that if the subject has more than two commas in it, it probably means something else'''
    help = "reprocess subjects containing ';' or starting with 'nyt:' or 'award:'"
    
    def handle(self, **options):
       semicolon_subjects = Subject.objects.filter(name__contains=";")

       for subject in semicolon_subjects:
            for work in subject.works.all():
                Subject.set_by_name(subject.name, work=work)
            subject.delete()

       nyt_subjects = Subject.objects.filter(name__startswith="nyt:")
       for subject in nyt_subjects:
            for work in subject.works.all():
                Subject.set_by_name(subject.name, work=work)
            subject.delete()

       award_subjects = Subject.objects.filter(name__startswith="award:")
       for subject in award_subjects:
            for work in subject.works.all():
                Subject.set_by_name(subject.name, work=work)
            subject.delete()

       period_subjects = Subject.objects.filter(name__contains=".")
       for subject in period_subjects:
            if not valid_subject(subject.name):
                subject.delete()
