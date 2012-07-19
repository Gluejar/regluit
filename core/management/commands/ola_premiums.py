from django.core.management.base import BaseCommand

import django
import sys
from regluit.core.models import Campaign
from regluit.payment.models import Transaction
from django.db.models import Q, F, Count, Sum, Max
from django.contrib.auth.models import User
from regluit.payment.manager import PaymentManager
from decimal import Decimal as D

from regluit.experimental.gutenberg import unicode_csv

OLA_PREMIUM_IDS = [1L, 97L, 2L, 98L, 3L, 99L, 4L, 15L, 18L, 65L]
OLA_PREMIUMS_AND_AMOUNTS = [(1L, D('1')), (97L, D('7')), (2L, D('25')), (98L, D('40')), (3L, D('50')), (99L, D('75')), (4L, D('100')), (15L, D('200')), (18L, D('500')), (65L, D('1000'))]
LEVELS = (D('0'), D('1'), D('7'), D('25'), D('40'), D('50'), D('75'), D('100'), D('200'), D('500'), D('1000'))

MATERIAL_PREMIUMS = [(1, "The unglued ebook delivered to your inbox."),
    (2, "You will have the choice of one free digital edition selected from our list of published titles. (Offer valid until 30 September 2012)"),
    (3, "You may select one free paperback edition or three free digital editions from our list of published titles. (Offer valid until 30 September 2012.)"),
    (4, "You may select one free hardback edition, or two free paperback editions, or six free digital editions from our list of published titles. (Offer valid until 30 September 2012.)"),
    (5, "A free printed paperback edition with personalised message from the author acknowledging your support."),
    ]

class Command(BaseCommand):
    help = "Displays data about how related to collecting information about premiums for Oral Literature in Africa"
    # args = "<filename> <username>"
    
    def handle(self, **options):
        # this is meant specifically for OLA -- check whether such a compaign is in the db
        c3 = Campaign.objects.get(id=3)
        print c3.name
        if c3.name != 'Oral Literature in Africa':
            sys.exit()
            
        # enumerate the various premiums and how many people have chosen them
        # confirm that there are the same premiums as assumed in operation
        assert set([p.id for p in c3.effective_premiums()]) == set(OLA_PREMIUM_IDS)
        assert set([(p.id, p.amount) for p in c3.effective_premiums()]) == set(OLA_PREMIUMS_AND_AMOUNTS)
        
        # go through all premium choices and list # of people who have chosen that premium
        
        print "number of pledgers that did not pick any premium", c3.transaction_set.filter(status='Complete').filter(premium__isnull=True).count()
                # need to handle those who did not pick any premiums separately
    
        for p in c3.transaction_set.filter(Q(status='Complete') & Q(premium__isnull=False)).order_by('premium__amount').values_list('premium', 'premium__amount').annotate(count_premium=Count('premium')):
            print p[0], p[1], p[2]            
  
        # who deliberately picked premiums at a value level equal to the pledge amount
        print "number of transactions with amount equal to premium amount", c3.transaction_set.filter(Q(status='Complete') & Q(premium__isnull=False)).filter(amount = F('premium__amount')).count()
            
        # confirm that no one has a premium valued greater than transaction
        assert c3.transaction_set.filter(Q(status='Complete') & Q(premium__isnull=False)).filter(amount__lt = F('premium__amount')).count() == 0

        # how many people deliberately chose premiums of lower value -- not correct -- have to calculate for a
        # given amount, the corresponding premium level
        
        for t in c3.transaction_set.filter(Q(status='Complete') & Q(premium__isnull=False)).values('id', 'amount', 'premium__amount'):
            max_qualified = max(filter(lambda x: x <= t['amount'], LEVELS))
            if max_qualified != t['premium__amount']:
                print t['id'], t['amount'], t['premium__amount'], max_qualified
        
        # ok -- let's now figure out what we would be prompting each person 
        
        