import string
from django.core.management.base import BaseCommand
from regluit.core.models import TWITTER

from regluit.core import models

class Command(BaseCommand):
    help = "fix old twitter avatar urls"
    
    def handle(self, **options):
        print "Number of users affected with : %s" % models.UserProfile.objects.filter( pic_url__contains='//si0.twimg.com').count()
        
        for profile in models.UserProfile.objects.filter(pic_url__contains='//si0.twimg.com'):
            print "updating user %s" % profile.user 
            profile.pic_url =  string.replace( profile.pic_url, '//si0.twimg.com','//pbs.twimg.com')
            profile.save()
