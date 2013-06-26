from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from regluit.core import tasks, bookloader
from regluit.core.goodreads import GoodreadsClient

#from regluit.core.goodreads import load_shelf_into_wishlist

class Command(BaseCommand):
    help = "list books on given user bookshelf"
    args = "<user_name goodreads_user_id shelf_name max_books>"
    
    def handle(self, user_name, goodreads_user_id, shelf_name, max_books, **options):
        
        user = User.objects.get(username=user_name)
        max_books = int(max_books)
        
        tasks.load_goodreads_shelf_into_wishlist.delay(user.id, shelf_name,  goodreads_user_id, max_books)