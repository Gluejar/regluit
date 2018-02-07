from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "grant (or debit or redeem) credit to a user"
    args = "<username> <amount> <action>"

    def handle(self, username, amount, action="credit", *args, **kwargs):
        if action not in ("debit", "redeem", "credit"):
            print 'action should be  in ("debit", "redeem", "credit")'
            return
        if action in ("debit", "redeem" ):
            amount = -int(amount)
        elif action == "credit":
            amount = int(amount)
        user = User.objects.get(username=username)
        notify = action != "redeem"
        user.credit.add_to_balance(amount, notify=notify)
        print "%s now has a balance of %s credits" % (username, user.credit.balance)
