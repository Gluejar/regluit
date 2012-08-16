from django.core.management.base import BaseCommand
from django.contrib.auth.models import User 

class Command(BaseCommand):
    help = "grant credit to a user"
    args = "<username> <amount> <action>"

    def handle(self, username, amount, action="credit", *args, **kwargs):
        if action=="debit":
            amount=-int(amount)
        else:
            amount= int(amount)
        user = User.objects.get(username=username)
        user.credit.add_to_balance(amount)
        print "%s now has a balance of %s donation credits" % (username, user.credit.balance)
     