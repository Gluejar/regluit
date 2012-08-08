"""
print user emails
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from regluit.core import models

class Command(BaseCommand):
    help = "dump all ungluer emails"
    
    def handle(self, **options):
        num=0
        
        for user in User.objects.all():
            print user.email
            num=num+1
        print "Number of emails= %s" % num
