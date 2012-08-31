from datetime import timedelta

from django.contrib.auth.models import User
from django.conf import settings

from regluit.payment.parameters import *
from regluit.utils.localdatetime import now
from regluit.payment.baseprocessor import BasePaymentRequest


def pledge_transaction(t,user,amount):
    """commit <amount> from a <user>'s credit to a specified transaction <t>"""
    
    if t.amount and t.host == PAYMENT_HOST_CREDIT:
        #changing the pledge_transaction
        user.credit.add_to_pledged(amount-t.amount)
    else:  
        user.credit.add_to_pledged(amount)
    t.amount=amount
    t.max_amount=amount
    t.host = PAYMENT_HOST_CREDIT
    t.type = PAYMENT_TYPE_AUTHORIZATION
    t.status=TRANSACTION_STATUS_ACTIVE
    t.approved=True
    now_val = now()
    t.date_authorized = now_val
    t.date_expired = now_val + timedelta( days=settings.PREAPPROVAL_PERIOD )

    t.save()

    
class CancelPreapproval(BasePaymentRequest):
    '''
        Cancels an exisiting token.  
    '''
    
    def __init__(self, transaction):
        self.transaction = transaction
        if transaction.user.credit.add_to_pledged(-transaction.amount):
            #success
            transaction.status=TRANSACTION_STATUS_CANCELED
            transaction.save()
        else:
            self.errorMessage="couldn't cancel the transaction"
            self.status = 'Credit Cancel Failure'

class PreapprovalDetails(BasePaymentRequest):
    status = None
    approved = None
    currency = None
    amount = None
    def __init__(self, transaction):
        self.status = transaction.status
        self.approved = transaction.approved
        self.currency = transaction.currency
        self.amount = transaction.amount
