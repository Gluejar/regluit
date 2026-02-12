from django.core.management.base import BaseCommand
from regluit.payment import stripelib
from decimal import Decimal as D

class Command(BaseCommand):
    help = "For monitoring stripe -- meant to be run on machine with transactions"

    def handle(self, *args, **kwargs):
        # TEST MODE first
        sc = stripelib.StripeClient(api_key=stripelib.TEST_STRIPE_SK)
        print [(i, e.id, e.type, e.created, e.pending_webhooks, e.data) for (i,e) in enumerate(sc.list_events())]
        print list(sc.list_customers())
        # what type of filtering?  How far does this go back?
        # there is a count and an offset -- nice to create a generator for this
