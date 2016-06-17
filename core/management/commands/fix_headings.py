from django.core.management.base import BaseCommand

from regluit.core.models import Subject



class Command(BaseCommand):
    '''funny syntax in yaml has resulted in spurious headings'''
    help = "fix subjects with authority tags in the name"
    
    def handle(self, **options):
        clean_headings('lcc')
        clean_headings('lcsh')
        clean_headings('bisac')

def clean_headings(authority):
   subjects = Subject.objects.filter(name__startswith="!{}:".format(authority))
   pos=len(authority)+2
   for subject in subjects:
        the_subject = subject.name[pos:].strip()
        new_subject = None
        for prev_subject in Subject.objects.filter(name=the_subject, authority=authority):
            new_subject = prev_subject
        if not new_subject:
            for prev_subject in Subject.objects.filter(name=the_subject):
                new_subject = prev_subject
                if not new_subject.authority:
                    new_subject.authority=authority
                    new_subject.save()
        if new_subject:
            for work in subject.works.all():
                new_subject.works.add(work)
            subject.delete()
            continue
        subject.name=the_subject 
        subject.authority=authority
        subject.save()
                
                
                
                
