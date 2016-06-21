"""
print user emails
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from regluit.core import models

class Command(BaseCommand):
    help = "claim books for rights_holder based on a text file of ISBNs"
    args = "<rights_holder_id> <filename>"

    def handle(self, rights_holder_id, filename, **options):
        try:
            rh = models.RightsHolder.objects.get(id=int(rights_holder_id))
        except models.Identifier.DoesNotExist:
            print '{} not a rights_holder'.format(rights_holder_id)
            return
        with open(filename) as f:
            for isbn in f:
                isbn = isbn.strip()
                try:
                    work = models.Identifier.objects.get(type='isbn',value=isbn).work
                    try: 
                        c = models.Claim.objects.get(work=work)
                        print '{} already claimed by {}'.format(work, c.rights_holder)
                    except models.Claim.DoesNotExist:
                        c = models.Claim.objects.create(
                            work=work, 
                            rights_holder=rh, 
                            user=rh.owner, 
                            status='active')
                        print '{} claimed for {}'.format(work, rh)
                except models.Identifier.DoesNotExist:
                    print '{} not loaded'.format(isbn)
                    continue
