from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User

from regluit.payment import baseprocessor
from regluit.payment.baseprocessor import BasePaymentRequest
from regluit.payment.parameters import *

def pledge_transaction(t,user,amount):
    """commit <amount> from a <user>'s credit to a specified transaction <t>"""
    
    if t.amount and t.host == PAYMENT_HOST_CREDIT:
        #changing the pledge_transaction
        success = user.credit.add_to_pledged(amount-t.amount)
    else:  
        success = user.credit.add_to_pledged(amount)
    if success:
        t.max_amount=amount
        t.set_credit_approved(amount)
    return success

def credit_transaction(t,user,amount):
    '''user has new credit, use it to fund the transaction'''
    # first, credit the user's account
    success = user.credit.add_to_balance(amount)
    if success:
        # now pledge to the transaction
        pledge_amount = t.max_amount if t.max_amount <= user.credit.available else amount
        success = user.credit.add_to_pledged(pledge_amount)
        if success:
            t.set_credit_approved(pledge_amount)
    return success

def pay_transaction(t, user, to_user, amount):
    '''user has credit, transfer it to rh account'''
    success = user.credit.transfer_to(to_user , amount)
    if success:
        t.set_executed()
    return success

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
