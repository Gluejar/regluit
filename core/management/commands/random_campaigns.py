from decimal import Decimal
from random import randint, randrange
from datetime import datetime, timedelta
from decimal import Decimal as D

from django.core.management.base import BaseCommand

from regluit.core.models import Work, Campaign
from django.conf import settings

class Command(BaseCommand):
    help = "creates random campaigns for any works that lack one for testing"

    def handle(self, *args, **options):
        for work in Work.objects.all():
            if work.campaigns.all().count() > 0:
                continue
            campaign = Campaign()
            campaign.name = work.title
            campaign.work = work
            campaign.description = "Test Campaign"

            # random campaign target between $200 and $10,000
            campaign.target = D(randint(200,10000))
            
            # add a test rightsholder recipient right now
            campaign.paypal_receiver = settings.PAYPAL_TEST_RH_EMAIL

            # random deadline between 5 days from now and 180 days from now
            now = datetime.now()
            campaign.deadline = random_date(now + timedelta(days=5),
                                            now + timedelta(days=180))

            # randomly activate some of the campaigns
            coinflip = D(randint(0,10))
            if coinflip > 5:
	            campaign.activated = now

            campaign.save()
            campaign.activate()
            print "activated campaign %s" % campaign


def random_date(start, end):
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return (start + timedelta(seconds=random_second))

