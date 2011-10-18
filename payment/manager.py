from regluit.core.models import Campaign, Wishlist
from regluit.payment.models import Transaction, Receiver
from django.contrib.auth.models import User
from regluit.payment.parameters import *
from regluit.payment.paypal import Pay, IPN, IPN_TYPE_PAYMENT, IPN_TYPE_PREAPPROVAL, IPN_TYPE_ADJUSTMENT, Preapproval, IPN_PAY_STATUS_COMPLETED, CancelPreapproval, IPN_SENDER_STATUS_COMPLETED, IPN_TXN_STATUS_COMPLETED
import uuid
import traceback
import logging
from decimal import Decimal as D

logger = logging.getLogger(__name__)

# at this point, there is no internal context and therefore, the methods of PaymentManager can be recast into static methods
class PaymentManager( object ): 

    def processIPN(self, request):
        '''
        processIPN
        
        Turns a request from Paypal into an IPN, and extracts info.   We support 2 types of IPNs:
        
        1) Payment - Used for instant payments and to execute pre-approved payments
        2) Preapproval - Used for comfirmation of a preapproval
        
        '''        
        try:
            ipn = IPN(request)
        
            if ipn.success():
                logger.info("Valid IPN")
    
                
                if ipn.transaction_type == IPN_TYPE_PAYMENT:
                    # payment IPN
                    
                    key = ipn.key()
                    t = Transaction.objects.get(reference=key)
                    
                    # The status is always one of the IPN_PAY_STATUS codes defined in paypal.py
                    t.status = ipn.status
                    
                    
                    for item in ipn.transactions:
                        
                        try:
                            r = Receiver.objects.get(transaction=t, email=item['receiver'])
                            logger.info(item)
                            # one of the IPN_SENDER_STATUS codes defined in paypal.py
                            r.status = item['status_for_sender_txn']
                            r.txn_id = item['id_for_sender_txn']
                            r.save()
                        except:
                            # Log an excecption if we have a receiver that is not found
                            traceback.print_exc()
                        
                    t.save()
                    
                elif ipn.transaction_type == IPN_TYPE_ADJUSTMENT:
                    # a chargeback, reversal or refund for an existng payment
                    
                    key = ipn.key()
                    t = Transaction.objects.get(reference=key)
                    
                    # The status is always one of the IPN_PAY_STATUS codes defined in paypal.py
                    t.status = ipn.status
                    
                    # Reason code indicates more details of the adjustment type
                    t.reason = ipn.reason_code
                    
                        
                elif ipn.transaction_type == IPN_TYPE_PREAPPROVAL:
                    
                   
                    key = ipn.key()
                    t = Transaction.objects.get(reference=key)
                    
                    # The status is always one of the IPN_PREAPPROVAL_STATUS codes defined in paypal.py
                    t.status = ipn.status
                    t.save()
                    logger.info("IPN: Preapproval transaction: " + str(t.id) + " Status: " + ipn.status)
                        
                else:
                    logger.info("IPN: Unknown Transaction Type: " + ipn.transaction_type)
                
                
            else:
                logger.info("ERROR: INVALID IPN")
                logger.info(ipn.error)
        
        except:
            traceback.print_exc()
         
    def run_query(self, transaction_list, summary, pledged, authorized ):
        '''
        Generic query handler for returning summary and transaction info,  see query_user, query_list and query_campaign
        '''

        if pledged:
            pledged_list = transaction_list.filter(type=PAYMENT_TYPE_INSTANT,
                                                   status="COMPLETED")
        else:
            pledged_list = []
        
        if authorized:
            authorized_list = Transaction.objects.filter(type=PAYMENT_TYPE_AUTHORIZATION,
                                                         status="ACTIVE")
        else:
            authorized_list = []
        
        if summary:
            pledged_amount = D('0.00')
            authorized_amount = D('0.00')
            
            for t in pledged_list:
                for r in t.receiver_set.all():
                    if r.status == IPN_TXN_STATUS_COMPLETED:
                        # or IPN_SENDER_STATUS_COMPLETED
                        # individual senders may not have been paid due to errors, and disputes/chargebacks only appear here
                        pledged_amount += r.amount
                
            for t in authorized_list:
                authorized_amount += t.amount
                
            amount = pledged_amount + authorized_amount
            return amount
        
        else:
            return pledged_list | authorized_list
        
           

    def query_user(self, user, summary=False, pledged=True, authorized=True):
        '''
        query_user
        
        Returns either an amount or list of transactions for a user
        
        summary: if true, return a float of the total, if false, return a list of transactions
        pledged: include amounts pledged
        authorized: include amounts pre-authorized
        
        return value: either a float summary or a list of transactions
        
        '''        
        
        transactions = Transaction.objects.filter(user=user)
        return self.run_query(transactions, summary, pledged, authorized)
       
    def query_campaign(self, campaign, summary=False, pledged=True, authorized=True):
        '''
        query_campaign
        
        Returns either an amount or list of transactions for a campaign
        
        summary: if true, return a float of the total, if false, return a list of transactions
        pledged: include amounts pledged
        authorized: include amounts pre-authorized
        
        return value: either a float summary or a list of transactions
        
        '''        
        
        transactions = Transaction.objects.filter(campaign=campaign)
        return self.run_query(transactions, summary, pledged, authorized)
    

    def query_list(self, list, summary=False, pledged=True, authorized=True):
        '''
        query_list
        
        Returns either an amount or list of transactions for a list
        
        summary: if true, return a float of the total, if false, return a list of transactions
        pledged: include amounts pledged
        authorized: include amounts pre-authorized
        
        return value: either a float summary or a list of transactions
        
        '''        
        
        transactions = Transaction.objects.filter(list=list)
        return self.run_query(transactions, summary, pledged, authorized)
            
    def execute_campaign(self, campaign):
        '''
        execute_campaign
        
        attempts to execute all pending transactions for a campaign. 
        
        return value: returns a list of transactions with the status of each receiver/transaction updated
        
        '''               
        
        # only allow active transactions to go through again, if there is an error, intervention is needed
        transactions = Transaction.objects.filter(campaign=campaign, status="ACTIVE")
        
        for t in transactions:
            
            # BUGBUG: Fill this in with the correct info from the campaign object
            receiver_list = [{'email':'jakace_1309677337_biz@gmail.com', 'amount':t.amount}, 
                            {'email':'seller_1317463643_biz@gmail.com', 'amount':t.amount * 0.20}]
            
            self.execute_transaction(t, receiver_list) 

        return transactions
    

    def execute_transaction(self, transaction, receiver_list):
        '''
        execute_transaction
        
        executes a single pending transaction.
        
        transaction: the transaction object to execute
        receiver_list: a list of receivers for the transaction, in this format:
        
                [
                    {'email':'email-1', 'amount':amount1}, 
                    {'email':'email-2', 'amount':amount2}
                ]
        
        return value: a bool indicating the success or failure of the process.  Please check the transaction status
        after the IPN has completed for full information
        
        '''        
        
        if len(transaction.receiver_set.all()) > 0:
            # we are re-submitting a transaction, wipe the old receiver list
            transaction.receiver_set.all().delete()
            
        transaction.create_receivers(receiver_list)
            
        p = Pay(transaction)
        
        # We will update our transaction status when we receive the IPN
        
        if p.status() == IPN_PAY_STATUS_COMPLETED:
            logger.info("Execute Success")
            return True
        
        else:
            transaction.error = p.error()
            logger.info("Execute Error: " + p.error())
            return False
    
    def cancel(self, transaction):
        '''
        cancel
        
        cancels a pre-approved transaction
        
        return value: True if successful, false otherwise
        '''        
        
        p = CancelPreapproval(transaction)
        
        if p.success():
            logger.info("Cancel Transaction " + str(transaction.id) + " Completed")
            return True
        
        else:
            logger.info("Cancel Transaction " + str(transaction.id) + " Failed with error: " + p.error())
            transaction.error = p.error()
            return False
        
    def authorize(self, currency, target, amount, campaign=None, list=None, user=None, return_url=None, cancel_url=None):
        '''
        authorize
        
        authorizes a set amount of money to be collected at a later date
        
        currency: a 3-letter paypal currency code, i.e. USD
        target: a defined target type, i.e. TARGET_TYPE_CAMPAIGN, TARGET_TYPE_LIST, TARGET_TYPE_NONE
        amount: the amount to authorize
        campaign: optional campaign object(to be set with TARGET_TYPE_CAMPAIGN)
        list: optional list object(to be set with TARGET_TYPE_LIST)
        user: optional user object
        
        return value: a tuple of the new transaction object and a re-direct url.  If the process fails,
                      the redirect url will be None
                      
        '''        
            
        t = Transaction.objects.create(amount=amount, 
                                       type=PAYMENT_TYPE_AUTHORIZATION, 
                                       target=target,
                                       currency=currency,
                                       secret = str(uuid.uuid1()),
                                       status='NONE',
                                       campaign=campaign,
                                       list=list,
                                       user=user
                                       )
        
        p = Preapproval(t, amount, return_url=return_url, cancel_url=cancel_url)
        
        if p.status() == 'Success':
            t.reference = p.paykey()
            t.save()
            logger.info("Authorize Success: " + p.next_url())
            return t, p.next_url()
        
        else:
            t.error = p.error()
            t.save()
            logger.info("Authorize Error: " + p.error())
            return t, None
        
    def pledge(self, currency, target, receiver_list, campaign=None, list=None, user=None, return_url=None, cancel_url=None):
        '''
        pledge
        
        Performs an instant payment
        
        currency: a 3-letter paypal currency code, i.e. USD
        target: a defined target type, i.e. TARGET_TYPE_CAMPAIGN, TARGET_TYPE_LIST, TARGET_TYPE_NONE
        receiver_list: a list of receivers for the transaction, in this format:
        
                [
                    {'email':'email-1', 'amount':amount1}, 
                    {'email':'email-2', 'amount':amount2}
                ]
        
        campaign: optional campaign object(to be set with TARGET_TYPE_CAMPAIGN)
        list: optional list object(to be set with TARGET_TYPE_LIST)
        user: optional user object
        
        return value: a tuple of the new transaction object and a re-direct url.  If the process fails,
                      the redirect url will be None
                      
        '''            
        
        amount = D('0.00')
        
        # for chained payments, first amount is the total amount
        amount = D(receiver_list[0]['amount'])
            
        t = Transaction.objects.create(amount=amount, 
                                       type=PAYMENT_TYPE_INSTANT, 
                                       target=target,
                                       currency=currency,
                                       secret = str(uuid.uuid1()),
                                       status='NONE',
                                       campaign=campaign,
                                       list=list,
                                       user=user
                                       )
    
        t.create_receivers(receiver_list)
        
        p = Pay(t,return_url=return_url, cancel_url=cancel_url)
        
        if p.status() == 'CREATED':
            t.reference = p.paykey()
            t.status = 'CREATED'
            t.save()
            logger.info("Pledge Success: " + p.next_url())
            return t, p.next_url()
        
        else:
            t.error = p.error()
            t.save()
            logger.info("Pledge Error: " + p.error())
            return t, None
    
    