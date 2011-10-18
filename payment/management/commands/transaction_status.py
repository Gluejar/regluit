from django.core.management.base import BaseCommand

import regluit
from pprint import pprint

class Command(BaseCommand):
    help = "show current status of transactions"

    def handle(self, *args, **kwargs):
        transactions = regluit.payment.models.Transaction.objects.all()
        for t in transactions:
            pd = regluit.payment.paypal.PaymentDetails(t)
            print pprint(pd.response)
            print pd.compare()
     