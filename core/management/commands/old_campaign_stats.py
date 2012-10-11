from django.core.management.base import BaseCommand

from django.db.models import Q, F, Count, Sum
from regluit.core.models import Campaign

STATS_TEMPLATE = """Total Pledged: {0} by {1} Pledgers

Distribution of Pledges:

{2}

Premiums Offered:

{3}

Premiums Selected:

{4}

Number of Transactions without premiums selected: {5}"""

def campaign_stats(c):
    # Use aggregations: https://docs.djangoproject.com/en/dev/topics/db/aggregation/#cheat-sheet    

    transactions = c.transaction_set.filter(Q(status='Canceled') & Q(reason ='Amazon FPS shutdown'))
    
    amount_sum = transactions.aggregate(Sum('amount'))['amount__sum']
    number_pledgers = transactions.count()
    
    # do we have unique 
    
    amount_table = "Level\tCount\tTotal\n" + "\n".join(["{0}\t{1}\t{2}".format(k['amount'], k['count_amount'], k['amount']*k['count_amount']) for k in transactions.values('amount').annotate(count_amount=Count('amount')).order_by('-amount')])

    # premiums offered
    
    premiums_offered = "id\tamount\tdescription\tcampaign_id\n" + "\n".join(["{0}\t{1}\t{2}\t{3}".format(p.id, p.amount, p.description, p.campaign_id) for p in c.effective_premiums()])

    transactions_null_premiums_count = transactions.filter(premium__isnull=True).count()

# list stats around premiums

    premium_selected = "Amount\tCount\tPrem. id\tDescription\n" + \
                       "\n".join(["{0}\t{1}\t{2}\t{3}".format(k['premium__amount'], k['count_premium'],
                                       k['premium'], k['premium__description']) for k in 
                       transactions.filter(premium__isnull=False).values('premium',
                                                  'premium__description', 'premium__amount').annotate(count_premium=Count(                       'premium')).order_by('premium__amount')])
    
    return(STATS_TEMPLATE.format(amount_sum, number_pledgers, amount_table, premiums_offered, premium_selected, transactions_null_premiums_count))

class Command(BaseCommand):
    help = "Displays data about old campaigns"
    # args = "<filename> <username>"
    
    def handle(self, **options):
    
        # Melinda's campaign
        c6 = Campaign.objects.get(id=6)
        print campaign_stats(c6)

