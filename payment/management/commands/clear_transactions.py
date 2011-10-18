from django.core.management.base import BaseCommand

import regluit
from pprint import pprint

class Command(BaseCommand):
    help = "clear all transactions"

    def handle(self, *args, **kwargs):
        transactions = regluit.payment.models.Transaction.objects.all()
        for t in transactions:
            t.delete()
     