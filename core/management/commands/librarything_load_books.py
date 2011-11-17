from django.core.management.base import BaseCommand
from regluit.core import librarything
from regluit.core import tasks
from django.conf import settings
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "load Librarything books into wishlist"
    args = "<user_name lt_username max_books>"
    
    def handle(self, user_name, lt_username, max_books, **options):
        
        user = User.objects.get(username=user_name)
        max_books = int(max_books)
        
        tasks.load_librarything_into_wishlist.delay(user, lt_username, max_books)