"""
one-time command to ensure transaction.ack_name for OLA returns something sensible
see https://github.com/Gluejar/regluit/pull/97#discussion_r2436193
"""

from django.core.management.base import BaseCommand
from regluit.core.models import Campaign
from regluit.payment.models import Transaction

class Command(BaseCommand):
    help = "make sure transaction.ack_name returns something sensible for OLA transactions"
    
    def handle(self, **options):
        ola_campaign = Campaign.objects.filter(work__id=81834)
        assert ola_campaign.count() == 1
        ola_campaign = ola_campaign[0]
        ola_transactions = Transaction.objects.filter(campaign=ola_campaign)
        for t in ola_transactions:
            if t.anonymous:
                t.extra.update({"ack_name": ''})
            else:
                ack_name=t.extra.get("ack_name",'')
                if not ack_name:
                    t.extra.update({"ack_name": t.user.username})
            t.extra.update({"ack_dedication":  ''})
            t.save()
