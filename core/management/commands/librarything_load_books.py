from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from regluit.core import librarything, tasks

class Command(BaseCommand):
    help = "load Librarything books into wishlist"
    args = "<user_name lt_username max_books>"
    
    def handle(self, user_name, lt_username, max_books, **options):
        
        user = User.objects.get(username=user_name)
        max_books = int(max_books)
        
        tasks.load_librarything_into_wishlist.delay(user.id, lt_username, max_books)