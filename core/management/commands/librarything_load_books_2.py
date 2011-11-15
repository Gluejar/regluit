from django.core.management.base import BaseCommand
from regluit.core import librarything
from regluit.core import tasks
from django.conf import settings
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "load Librarything books into wishlist"
    args = "<lt_username>"
    
    def handle(self, lt_username, **options):
        
        lt = librarything.LibraryThing(username=lt_username)
        for (i, book) in enumerate(lt.parse_user_catalog()):
            print i, book["title"]
        