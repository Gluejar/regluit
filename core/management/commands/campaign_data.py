from django.core.management.base import BaseCommand


from regluit.core.models import Campaign
from regluit.payment.models import Transaction
from django.db.models import Q, F, Count, Sum, Max
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Displays data about how the campaigns are progressing"
    # args = "<filename> <username>"
    
    def handle(self, **options):
        # what campaigns are active
        print "Number of active campaigns ", Campaign.objects.filter(status='Active').count()
        # number of active transactions
        print "Number of active transactions ", Transaction.objects.filter(status='Active').count()
        
        # breakdown of Transactions by status
        print "breakdown by transaction status", Transaction.objects.values('status').annotate(count_status=Count('status'))
        
        # distribution of donations for *Oral Literature*
        c3 = Campaign.objects.get(id=3)
        print "number of active transactions for Oral Lit", c3.transaction_set.filter(status='Active').count()
        
        # total amount -- how to do a straight up sum?
        print c3.transaction_set.filter(status='Active').aggregate(Sum('amount'))
        print c3.transaction_set.filter(status='Active').aggregate(Max('amount'))
        
        # distribution?
        clusters = c3.transaction_set.filter(status='Active').values('amount').annotate(count_amount=Count('amount')).order_by('-amount')
        for t in clusters:
            print "{0}\t{1}\t{2}".format(t['amount'], t['count_amount'], t['count_amount']*t['amount'])
        #print [(t['amount'], t['count_amount']*t['amount']) for t in clusters]
    
        # donors sorted by donation and time
        # top 10
        
        c3_users = set([u[0] for u in c3.transaction_set.values_list('user__username')])
        
        # 0 or 1 Active
        # 0 or 1 Complete
        # Created? -- outmoded
        # any number of NONE
        # any number of Canceled
        # if there is an Active transaction, it should be the very last one.
        
        c3_users_active_t = set([u[0] for u in c3.transaction_set.filter(status='Active').values_list('user__username')])
        [(u, c3.transaction_set.filter(user__username=u).values_list('status').order_by('-date_created')[0]) for u in c3_users_active_t]
        # pull up latest transaction by user

        # is there only one and only one active transaction for a user who has pledged?
        
        # users who have more than one transaction with c3
        users_multi_trans = c3.transaction_set.values_list('user__username').annotate(user_count=Count('user')).filter(user_count__gt=1)
        # NONE status -- follow up on?
        
        
        # who has modified a transaction and never cancelled it?

