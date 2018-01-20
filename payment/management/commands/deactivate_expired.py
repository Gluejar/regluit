from django.core.management.base import BaseCommand

from regluit.payment.models import Account

class Command(BaseCommand):
    help = "deactivate accounts that have expired"

    def handle(self, *args, **kwargs):
        expired = Account.objects.filter(status='EXPIRED', date_deactivated__isnull=True)
        for account in expired:
            account.deactivate()
     