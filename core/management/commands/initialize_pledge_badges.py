"""
set the 'pledged' badge for people who've pledged
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from regluit.core.models import Badge
from regluit.payment.models import Transaction

class Command(BaseCommand):
    help = "for people who've pledged, give them a badge!"

    
    def handle(self, **options):
        pledger= Badge.objects.get(name='pledger')
        pledger2= Badge.objects.get(name='pledger2')
        print 'start'
        print 'pledger badges: %s' % pledger.holders.all().count()
        print 'pledger2 badges: %s' % pledger2.holders.all().count()
        pledges=Transaction.objects.exclude(status='NONE').exclude(status='Canceled',reason=None).exclude(anonymous=True)
        for pledge in pledges:
            if pledge.user.profile.badges.all().count():
                if pledge.user.profile.badges.all()[0].id == pledger.id:
                    pledge.user.profile.badges.remove(pledger)
                    pledge.user.profile.badges.add(pledger2)
            else:
                pledge.user.profile.badges.add(pledger)
        print 'end'
        print 'pledger badges: %s' % pledger.holders.all().count()
        print 'pledger2 badges: %s' % pledger2.holders.all().count()

        
            
            
