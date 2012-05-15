from django.core.management.base import BaseCommand
from regluit.payment.parameters import TRANSACTION_STATUS_ACTIVE
from regluit.core import models
from django.db.models import Q, F

class Command(BaseCommand):
    help = "Do some integrity checks on our Payments"
    
    def handle(self, **options):
        print "number of Campaigns", models.Campaign.objects.count()
        print "number of active Campaigns", models.Campaign.objects.filter(status='ACTIVE').count()
        for campaign in models.Campaign.objects.filter(status='ACTIVE'):
            print stats_for_active_campaign(campaign)
        
def stats_for_active_campaign(campaign):
    # might need to calculate 'number of users with more than 1 ACTIVE transaction (should be 0)'
    # set([t.user for t in c.transaction_set.filter(status='Active')]) - set(userlists.supporting_users(c.work,1000))
    # everyone with an ACTIVE pledge should have the work on his/her wishlist
    # set([w.user for w in c.work.wishlists.all()])
    # set([t.user for t in campaign.transaction_set.filter(status=TRANSACTION_STATUS_ACTIVE)]) - set([w.user for w in c.work.wishlists.all()])
    return {'name': campaign.name,
            'work':campaign.work,
            'number of ACTIVE transactions':campaign.transaction_set.filter(status=TRANSACTION_STATUS_ACTIVE).count(),
            'number of users with ACTIVE transactions': len(set([t.user for t in campaign.transaction_set.filter(status=TRANSACTION_STATUS_ACTIVE)])),
            'total amount of pledges in ACTIVE transactions': sum([t.amount for t in campaign.transaction_set.filter(status=TRANSACTION_STATUS_ACTIVE)]),
            }