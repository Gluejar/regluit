from django.core.management.base import BaseCommand

import regluit

class Command(BaseCommand):
    help = "retotal all campaigns"

    def handle(self, *args, **kwargs):
        campaigns = regluit.payment.models.Campaign.objects.all()
        for c in campaigns:
            c.update_left()
            print c.left
     