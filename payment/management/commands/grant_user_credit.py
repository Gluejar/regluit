from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

ACTIONS = ("debit", "redeem", "credit", "cash")
class Command(BaseCommand):
    help = "grant (or debit or redeem) credit to a user. \
    Usage: grant_user_credit <username> <amount> <action>\
    amount is dollars or 'all' "

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help="user to credit")    
        parser.add_argument('amount', type=str, help="amount to credit")    
        parser.add_argument('action', type=str, help="credit/debit/redeem/cash")    

    def handle(self, username, amount, action, **options):
        if action not in ACTIONS:
            self.stdout.write('action should be  in %s' % str(ACTIONS))
            return
        user = User.objects.get(username=username)
        if amount == 'all':
            amount = user.credit.available
        if action == 'redeem':
            user.credit.use_pledge(amount)
        else:
            amount = Decimal(amount)
            if action in ("debit", "cash"):
                amount = - amount
            user.credit.add_to_balance(amount, notify=action != "cash")
        self.stdout.write("{}ed ${} from {}".format(action, amount, username))
        self.stdout.write("{} now has a balance of {} credits".format(
            username, user.credit.balance))
