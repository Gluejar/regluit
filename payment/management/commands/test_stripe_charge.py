from decimal import Decimal as D

from django.core.management.base import BaseCommand

from regluit.payment import stripelib

class Command(BaseCommand):
    help = "create a credit card record and charge it -- for testing"

    def handle(self, *args, **kwargs):
        # test card
        sc = stripelib.StripeClient()
        card = stripelib.card(number="4242424242424242", exp_month="01", exp_year="2013", cvc="123")
        cust = sc.create_customer(card=card, description="William Shakespeare XIV (via test_stripe_charge)", email="bill.shakespeare@gmail.com")
        print cust
        # let's charge RY $1.00
        charge = sc.create_charge(D('1.00'), customer=cust.id, description="$1 TEST CHARGE for Will S. XIV")
        print charge