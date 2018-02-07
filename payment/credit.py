from datetime import datetime

from regluit.payment import baseprocessor
from regluit.payment.baseprocessor import BasePaymentRequest
from regluit.payment.parameters import (
    PAYMENT_HOST_CREDIT,
    PAYMENT_TYPE_AUTHORIZATION,
    PAYMENT_TYPE_INSTANT,
    TRANSACTION_STATUS_COMPLETE,
    TRANSACTION_STATUS_CANCELED,
)
from regluit.payment.signals import transaction_charged

def pledge_transaction(t, user, amount):
    """commit <amount> from a <user>'s credit to a specified transaction <t>"""

    if t.amount and t.host == PAYMENT_HOST_CREDIT:
        #changing the pledge_transaction
        success = user.credit.add_to_pledged(amount-t.amount)
    else:
        success = user.credit.add_to_pledged(amount)
    if success:
        t.type = PAYMENT_TYPE_AUTHORIZATION
        t.max_amount = amount
        t.set_credit_approved(amount)
    return success

def credit_transaction(t, user, amount):
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
    success = user.credit.transfer_to(to_user, amount)
    if success:
        t.type = PAYMENT_TYPE_INSTANT
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
                transaction.status = TRANSACTION_STATUS_CANCELED
                transaction.save()
            else:
                self.errorMessage = "couldn't cancel the transaction"
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

    class Execute(BasePaymentRequest):
        '''
            This Execute function debits the user credits and pledge and credits the recipient.
        '''
        def __init__(self, transaction=None):
            self.transaction = transaction
            amount = transaction.amount
            # make sure transaction hasn't already been executed
            if transaction.status == TRANSACTION_STATUS_COMPLETE:
                return

            used = transaction.user.credit.use_pledge(amount)
            if used:
                user_to_pay = transaction.campaign.user_to_pay
                credited = user_to_pay.credit.add_to_balance(amount, notify=False)
                transaction.status = TRANSACTION_STATUS_COMPLETE
                transaction.date_payment = datetime.now()
                transaction.save()

                # fire signal for sucessful transaction
                transaction_charged.send(sender=self, transaction=transaction)
