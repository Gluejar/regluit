from django.core.management.base import BaseCommand
from regluit.core.models import Campaign

class Command(BaseCommand):
    help = "set campaign edition for every campaign"
    
    def handle(self, **options):
        fixed = 0
        for campaign in Campaign.objects.all():
            if not campaign.edition:
                campaign.edition = campaign.work.editions.all()[0]
                campaign.save()
                fixed +=1
        print "{} campaign editions set".format(fixed)
