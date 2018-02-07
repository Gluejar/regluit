from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "grant (or debit or redeem) credit to a user. \
    Usage: grant_user_credit <username> <amount> <action>\
    amount is dollars or 'all' "
    args = "<username> <amount> <action>"

    def handle(self, username, amount, action="credit", *args, **kwargs):
        if action not in ("debit", "redeem", "credit"):
            print 'action should be  in ("debit", "redeem", "credit")'
            return
        user = User.objects.get(username=username)
        if amount == 'all':
            amount = user.credit.available
        if action in ("debit", "redeem" ):
            amount = -int(amount)
        elif action == "credit":
            amount = int(amount)
        notify = action != "redeem"
        user.credit.add_to_balance(amount, notify=notify)
        print "{}ed ${} from {}".format(action, amount, username)
        print "{} now has a balance of {} credits".format(username, user.credit.balance)
