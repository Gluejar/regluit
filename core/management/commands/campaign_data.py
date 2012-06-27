from django.core.management.base import BaseCommand

import django
from regluit.core.models import Campaign
from regluit.payment.models import Transaction
from django.db.models import Q, F, Count, Sum, Max
from django.contrib.auth.models import User
from regluit.payment.manager import PaymentManager

from regluit.experimental.gutenberg import unicode_csv

def amazon_payments(fname=r"/Users/raymondyee/Downloads/All-Activity-Jan-25-2012-Jun-25-2012.csv"):
    r0 = unicode_csv.UnicodeReader(f=open(fname), encoding="iso-8859-1")
    # grab the header
    header = r0.next()
    r = unicode_csv.UnicodeDictReader(f=open(fname), fieldnames=header, encoding="iso-8859-1")
    return dict([(k['Transaction ID'],k) for k in r])
    
def transactions_with_payment_info(transactions, payments=None):
    """an iterator for transactions / if a dict representing the actual payment data is provided, correlate the two"""
    for t in transactions:
        data = {"username":t.user.username,
                "email":t.user.email,
                "campaign_id": t.campaign.id if t.campaign is not None else None, 
                "amount":t.amount,
                "status":t.status,
                "local_status":t.local_status,
                "preapproval_key":t.preapproval_key,
                "approved":t.approved,
                "error":t.error}
        if payments is not None:
            payment = payments.get(t.preapproval_key, None)
            if payment is not None:
                data.update({'payment_transaction_id':payment['Transaction ID'],
                             'payment_name': payment['Name'],
                             'payment_status': payment['Status'],
                             'payment_amount': payment['Amount'],
                             'payment_fees': payment['Fees']
                             })
            else:
                data.update({'payment_transaction_id':None})
        else:
            data.update({'payment_transaction_id':None})
        yield data
    
    
def stats_for_campaign(c):
    print "transactions by statuses", c.transaction_set.values('status').annotate(count_status=Count('status'))
     
    # total amount -- aggregate transactions that are Complete, Active, Pending, Error, Failed
    valid_trans = c.transaction_set.filter(Q(status='Complete') | Q(status='Active') | Q(status='Pending') | Q(status='Error') | Q(status='Failed') )
    
    print "total amount for valid transactions", valid_trans.aggregate(Sum('amount'))['amount__sum']
    print "maximum amount for valid transactions", valid_trans.aggregate(Max('amount'))['amount__max']
    print 
    
    # distribution?
    clusters = valid_trans.values('amount').annotate(count_amount=Count('amount')).order_by('-amount')
    for t in clusters:
        print "{0}\t{1}\t{2}".format(t['amount'], t['count_amount'], t['count_amount']*t['amount'])
    #print [(t['amount'], t['count_amount']*t['amount']) for t in clusters]
    
    # calculate the problematic pledges
    problem_trans = c.transaction_set.filter(Q(status='Pending') | Q(status='Error') | Q(status='Failed'))

    # first list all the problem pledges
    for (i, t) in enumerate(problem_trans):
        print i, t.user, t.amount, t.status, t.local_status, t.preapproval_key, t.approved, t.error
        
    # let's consider the Error ones first

    # donors sorted by donation and time
    # top 10
    
    c_users = set([u[0] for u in c.transaction_set.values_list('user__username')])
    
    # 0 or 1 Active
    # 0 or 1 Complete
    # Created? -- outmoded
    # any number of NONE
    # any number of Canceled
    # if there is an Active transaction, it should be the very last one.
    
    c_users_active_t = set([u[0] for u in c.transaction_set.filter(status='Active').values_list('user__username')])
    [(u, c.transaction_set.filter(user__username=u).values_list('status').order_by('-date_created')[0]) for u in c_users_active_t]
    # pull up latest transaction by user

    # is there only one and only one active transaction for a user who has pledged?
    
    # users who have more than one transaction with c
    users_multi_trans = c.transaction_set.values_list('user__username').annotate(user_count=Count('user')).filter(user_count__gt=1)
    # NONE status -- follow up on?
    
    # tally up different classes of statuses we have for c
    
    # who has modified a transaction and never cancelled it?


class Command(BaseCommand):
    help = "Displays data about how the campaigns are progressing"
    # args = "<filename> <username>"
    
    def handle(self, **options):
        # what campaigns are active
        # List the campaigns
        for c in Campaign.objects.all():
            print c.name, c.status
        
        print
        
        # tally up the number of Campaigns with various statuses
        print Campaign.objects.values('status').annotate(count_status=Count('status'))
        print 
        
        # breakdown of Transactions by status
        print "transactions by status", Transaction.objects.values('status').annotate(count_status=Count('status'))
        
        # distribution of donations for *Oral Literature*
        print "stats for Oral Literature in Africa"
        
        c3 = Campaign.objects.get(id=3)
        stats_for_campaign(c3)
        
        out_fname = "/Users/raymondyee/Downloads/unglue_it_trans.csv"
        out_headers = ["username", 
                "email",
                "campaign_id",
                "amount",
                "status",
                "local_status",
                "preapproval_key",
                "approved",
                "error",
                "payment_transaction_id"
                ]
        
        f = open(out_fname, "wb")
        transactions = c3.transaction_set.filter(Q(status='Complete') | Q(status='Active') | Q(status='Pending') | Q(status='Error') | Q(status='Failed') )
        f = unicode_csv.output_to_csv(f, out_headers, transactions_with_payment_info(transactions, payments = amazon_payments()))
        
        
 