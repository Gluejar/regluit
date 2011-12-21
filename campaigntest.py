from regluit.core import models
from regluit.payment.models import Transaction
from regluit.payment.manager import PaymentManager
from regluit.payment.paypal import IPN_PAY_STATUS_ACTIVE, IPN_PAY_STATUS_INCOMPLETE, IPN_PAY_STATUS_COMPLETED

pm = PaymentManager()

def campaign_display():
    
    campaigns_with_active_transactions = models.Campaign.objects.filter(transaction__status=IPN_PAY_STATUS_ACTIVE)
    campaigns_with_incomplete_transactions = models.Campaign.objects.filter(transaction__status=IPN_PAY_STATUS_INCOMPLETE)
    campaigns_with_completed_transactions = models.Campaign.objects.filter(transaction__status=IPN_PAY_STATUS_COMPLETED)
    
    print "campaigns with active transactions", campaigns_with_active_transactions
    print "campaigns with incomplete transactions", campaigns_with_incomplete_transactions
    print "campaigns with completed transactions", campaigns_with_completed_transactions
    
def campaigns_active():
    return models.Campaign.objects.filter(transaction__status=IPN_PAY_STATUS_ACTIVE)

def campaigns_incomplete():
    return models.Campaign.objects.filter(transaction__status=IPN_PAY_STATUS_INCOMPLETE)
    
def campaigns_completed():
    return models.Campaign.objects.filter(transaction__status=IPN_PAY_STATUS_COMPLETED)

def execute_campaigns(clist):
    return [pm.execute_campaign(c) for c in clist]
    
def finish_campaigns(clist):
    return [pm.finish_campaign(c) for c in clist]

def drop_all_transactions():
    Transaction.objects.all().delete()
    # go through all Campaigns and set the self.left = self.target
    for c in models.Campaign.objects.all():
        c.left = c.target
        c.save()


# by the time we've executed a campaign, we should have r.status = 'COMPLETED' for primary but None for secondary
# [[[r.status  for r in t.receiver_set.all()]  for t in c.transaction_set.all()]  for c in campaigns_incomplete()]

# [[[r.status  for r in t.receiver_set.all()]  for t in c.transaction_set.all()]  for c in campaigns_completed()]

# res = [pm.finish_campaign(c) for c in campaigns_incomplete()]

