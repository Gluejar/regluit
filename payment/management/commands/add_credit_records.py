from django.core.management.base import BaseCommand
from django.contrib.auth.models import User 

import regluit.payment 

class Command(BaseCommand):
    help = "initialize credit table"

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        for user in users:
            regluit.payment.models.Credit(user=user).save()
     