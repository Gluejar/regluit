from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User

from regluit.core import bookloader


class Command(BaseCommand):
    help = "initialize test data"

    def handle(self, **options):
        
        # create PW2M book 
        w = bookloader.add_by_isbn('9781590598580')
        print(w) 

        # create test user
        user = User.objects.create_user(username=settings.UNGLUEIT_TEST_USER,
                                 email= settings.UNGLUEIT_TEST_EMAIL,
                                 password=settings.UNGLUEIT_TEST_PASSWORD)
        print (user)