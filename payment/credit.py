from datetime import timedelta

from django.contrib.auth.models import User
from django.conf import settings

from regluit.payment.parameters import *
from regluit.payment import baseprocessor
from regluit.payment.baseprocessor import BasePaymentRequest


def pledge_transaction(t,user,amount):
    """commit <amount> from a <user>'s credit to a specified transaction <t>"""
    
    if t.amount and t.host == PAYMENT_HOST_CREDIT:
        #changing the pledge_transaction
        user.credit.add_to_pledged(amount-t.amount)
    else:  
        user.credit.add_to_pledged(amount)
    t.max_amount=amount
    t.set_credit_approved(amount)

def credit_transaction(t,user,amount):
    '''user has new credit, use it to fund the transaction'''
    # first, credit the user's account
    user.credit.add_to_balance(amount)
    
    # now pledge to the transaction
    pledge_amount = t.max_amount if t.max_amount <= user.credit.available else amount
    user.credit.add_to_pledged(pledge_amount)
    t.set_credit_approved(pledge_amount)

class Processor(baseprocessor.Processor):
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
