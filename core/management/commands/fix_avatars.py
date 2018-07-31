import string
from django.core.management.base import BaseCommand
from regluit.core.models import FACEBOOK, UNGLUEITAR
from regluit.libraryauth.auth import pic_storage_url

from regluit.core import models

class Command(BaseCommand):
    help = "fix avatar urls and settings"
    
    def handle(self, **options):
        for profile in models.UserProfile.objects.exclude(pic_url=''):
            self.stdout.write("updating user %s" % profile.user)
            if not profile.pic_url.startswith('https://unglueit'):
                profile.pic_url = pic_storage_url(profile.user, 'twitter', profile.pic_url)
            profile.save()
        for profile in models.UserProfile.objects.filter(avatar_source=FACEBOOK):
            self.stdout.write("updating user %s" % profile.user)
            profile.facebook_id = ''
            if not profile.pic_url:
                profile.avatar_source = UNGLUEITAR
            profile.save()
