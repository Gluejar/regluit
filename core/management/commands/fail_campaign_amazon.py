"""
print user emails
"""

from django.core.management.base import BaseCommand
from regluit.core import models, signals

class Command(BaseCommand):
    help = "set active campaigns to unsuccessful"
    
    def handle(self, **options):
        for campaign in models.Campaign.objects.filter(status='ACTIVE'):
            campaign.status = 'UNSUCCESSFUL'
            campaign.save()
            action = models.CampaignAction(campaign=campaign, type='failed', comment = 'amazon suspension') 
            action.save()
            signals.amazon_suspension.send(sender=None,campaign=campaign)
            print 'campaign %s set to UNSUCCESSFUL' % campaign.id          
