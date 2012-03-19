from regluit.core.models import Campaign, Wishlist
from regluit.payment.models import Transaction, Receiver, PaymentResponse
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from regluit.payment.parameters import *
from regluit.payment.paypal import Pay, Execute, IPN, IPN_TYPE_PAYMENT, IPN_TYPE_PREAPPROVAL, IPN_TYPE_ADJUSTMENT, IPN_PAY_STATUS_ACTIVE, IPN_PAY_STATUS_INCOMPLETE, IPN_PAY_STATUS_NONE 
from regluit.payment.paypal import Preapproval, IPN_PAY_STATUS_COMPLETED, CancelPreapproval, PaymentDetails, PreapprovalDetails, IPN_SENDER_STATUS_COMPLETED, IPN_TXN_STATUS_COMPLETED
from regluit.payment.paypal import RefundPayment
import uuid
import traceback
from regluit.utils.localdatetime import now
from dateutil.relativedelta import relativedelta
import logging
from decimal import Decimal as D
from xml.dom import minidom
import urllib, urlparse

from django.conf import settings


logger = logging.getLogger(__name__)

def append_element(doc, parent, name, text):
    
    element = doc.createElement(name)
    parent.appendChild(element)
    text_node = doc.createTextNode(text)
    element.appendChild(text_node)
    
    return element

# at this point, there is no internal context and therefore, the methods of PaymentManager can be recast into static methods
class PaymentManager( object ): 
    
    def __init__( self, embedded=False):
        self.embedded = embedded

    def update_preapproval(self, transaction):
        """Update a transaction to hold the data from a PreapprovalDetails on that transaction"""
        t = transaction
        p = PreapprovalDetails(t)
                    
        preapproval_status = {'id':t.id, 'key':t.preapproval_key}
        
        if p.error() or not p.success():
            logger.info("Error retrieving preapproval details for transaction %d" % t.id)
            preapproval_status["error"] = "An error occurred while verifying this transaction, see server logs for details"
        else:
            
            # Check the transaction status
            if t.status != p.status:
                preapproval_status["status"] = {'ours':t.status, 'theirs':p.status}
                t.status = p.status
                t.save()
                
            # check the currency code
            if t.currency != p.currency:
                preapproval_status["currency"] = {'ours':t.currency, 'theirs':p.currency}
                t.currency = p.currency
                t.save()
                
            # Check the amount
            if t.max_amount != D(p.amount):
                preapproval_status["amount"] = {'ours':t.max_amount, 'theirs':p.amount}
                t.max_amount = p.amount
                t.save()
                
            # Check approved
            if t.approved != p.approved:
                preapproval_status["approved"] = {'ours':t.approved, 'theirs':p.approved}
                t.approved = p.approved
                t.save()
            
        
        return preapproval_status            

    def update_payment(self, transaction):
        """Update a transaction to hold the data from a PaymentDetails on that transaction"""
        t = transaction
        payment_status = {'id':t.id}
            
        p = PaymentDetails(t)
        
        if p.error() or not p.success():
            logger.info("Error retrieving payment details for transaction %d" % t.id)
            payment_status['error'] = "An error occurred while verifying this transaction, see server logs for details"
        else:
            
            # Check the transaction status
            if t.status != p.status:
                payment_status['status'] = {'ours': t.status, 'theirs': p.status}
                
                t.status = p.status
                t.save()
                
            receivers_status = []
            
            for r in p.transactions:
                
                try:
                    receiver = Receiver.objects.get(transaction=t, email=r['email'])
                    
                    receiver_status = {'email':r['email']}
                    
                    logger.info(r)
                    logger.info(receiver)
                    
                    # Check for updates on each receiver's status.  Note that unprocessed delayed chained payments
                    # will not have a status code or txn id code
                    if receiver.status != r['status']:
                        receiver_status['status'] = {'ours': receiver.status, 'theirs': r['status']}
                        receiver.status = r['status']
                        receiver.save()
                        
                    if receiver.txn_id != r['txn_id']:
                        receiver_status['txn_id'] = {'ours':receiver.txn_id, 'theirs':r['txn_id']}
                        
                        receiver.txn_id = r['txn_id']
                        receiver.save()
                        
                except:
                    traceback.print_exc()
                    
                if not set(["status","txn_id"]).isdisjoint(receiver_status.keys()):   
                    receivers_status.append(receiver_status)
            
            if len(receivers_status):
                payment_status["receivers"] = receivers_status
                
        return payment_status

    
    def checkStatus(self, past_days=None, transactions=None):
        
        '''
        Run through all pay transactions and verify that their current status is as we think.
        
        Allow for a list of transactions to be passed in or for the method to check on all transactions within the
        given past_days
        
        '''
        
        DEFAULT_DAYS_TO_CHECK = 3
        
        status = {'payments':[], 'preapprovals':[]}
        
        # look at all PAY transactions for stated number of past days; if past_days is not int, get all Transaction
        # only PAY transactions have date_payment not None
        
        if transactions is None:
            
            if past_days is None:
                past_days = DEFAULT_DAYS_TO_CHECK
        
            try:
                ref_date = now() - relativedelta(days=int(past_days))
                payment_transactions = Transaction.objects.filter(date_payment__gte=ref_date)
            except:
                ref_date = now()
                payment_transactions = Transaction.objects.filter(date_payment__isnull=False)
                
            logger.info(payment_transactions)
            
            # Now look for preapprovals that have not been paid and check on their status
            preapproval_transactions = Transaction.objects.filter(date_authorized__gte=ref_date, date_payment=None, type=PAYMENT_TYPE_AUTHORIZATION)
    
            logger.info(preapproval_transactions)
            
            transactions = payment_transactions | preapproval_transactions
 
        
        for t in transactions:
            
            if t.date_payment is None:
                preapproval_status = self.update_preapproval(t)            
                if not set(['status', 'currency', 'amount', 'approved']).isdisjoint(set(preapproval_status.keys())):
                    status["preapprovals"].append(preapproval_status)
            else:
                payment_status = self.update_payment(t)                    
                if not set(["status", "receivers"]).isdisjoint(payment_status.keys()):
                    status["payments"].append(payment_status)
            
        return status
    
        
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
                logger.info("IPN Transaction Type: %s" % ipn.transaction_type)
                
                if ipn.transaction_type == IPN_TYPE_PAYMENT:
                    # payment IPN. we use our unique reference for the transaction as the key
                    # is only valid for 3 hours
                    
                    uniqueID = ipn.uniqueID()
                    t = Transaction.objects.get(secret=uniqueID)
                    
                    # The status is always one of the IPN_PAY_STATUS codes defined in paypal.py
                    t.status = ipn.status
                    
                    
                    for item in ipn.transactions:
                        
                        try:
                            r = Receiver.objects.get(transaction=t, email=item['receiver'])
                            logger.info(item)
                            # one of the IPN_SENDER_STATUS codes defined in paypal.py,  If we are doing delayed chained
                            # payments, then there is no status or id for non-primary receivers.  Leave their status alone
                            r.status = item['status_for_sender_txn']
                            r.txn_id = item['id_for_sender_txn']
                            r.save()
                        except:
                            # Log an exception if we have a receiver that is not found.  This will be hit
                            # for delayed chained payments as there is no status or id for the non-primary receivers yet
                            traceback.print_exc()
                    
                    t.save()
                    
                    logger.info("Final transaction status: %s" % t.status)
                    
                elif ipn.transaction_type == IPN_TYPE_ADJUSTMENT:
                    # a chargeback, reversal or refund for an existng payment

                    uniqueID = ipn.uniqueID()
                    if uniqueID:
                        t = Transaction.objects.get(secret=uniqueID)
                    else:
                        key = ipn.pay_key
                        t = Transaction.objects.get(pay_key=key)
                    
                    # The status is always one of the IPN_PAY_STATUS codes defined in paypal.py
                    t.status = ipn.status
                    
                    # Reason code indicates more details of the adjustment type
                    t.reason = ipn.reason_code
        
                    # Update the receiver status codes
                    for item in ipn.transactions:
                        
                        try:
                            r = Receiver.objects.get(transaction=t, email=item['receiver'])
                            logger.info(item)
                            # one of the IPN_SENDER_STATUS codes defined in paypal.py,  If we are doing delayed chained
                            # payments, then there is no status or id for non-primary receivers.  Leave their status alone
                            r.status = item['status_for_sender_txn']
                            r.save()
                        except:
                            # Log an exception if we have a receiver that is not found.  This will be hit
                            # for delayed chained payments as there is no status or id for the non-primary receivers yet
                            traceback.print_exc()
                            
                    t.save()                    
                    
                        
                elif ipn.transaction_type == IPN_TYPE_PREAPPROVAL:
                    
                    # IPN for preapproval always uses the key to ref the transaction as this is always valid
                    key = ipn.preapproval_key
                    t = Transaction.objects.get(preapproval_key=key)
                    
                    # The status is always one of the IPN_PREAPPROVAL_STATUS codes defined in paypal.py
                    t.status = ipn.status
                    
                    # capture whether the transaction has been approved
                    t.approved = ipn.approved
                    
                    t.save()
                    logger.info("IPN: Preapproval transaction: " + str(t.id) + " Status: " + ipn.status)
                        
                else:
                    logger.info("IPN: Unknown Transaction Type: " + ipn.transaction_type)
                
                
            else:
                logger.info("ERROR: INVALID IPN")
                logger.info(ipn.error)
        
        except:
            traceback.print_exc()
         
    def run_query(self, transaction_list, summary, pledged, authorized, incomplete, completed):
        '''
        Generic query handler for returning summary and transaction info,  see query_user, query_list and query_campaign
        '''

        if pledged:
            pledged_list = transaction_list.filter(type=PAYMENT_TYPE_INSTANT,
                                                   status=IPN_PAY_STATUS_COMPLETED)
        else:
            pledged_list = []
        
        if authorized:
            # return only ACTIVE transactions with approved=True
            authorized_list = transaction_list.filter(type=PAYMENT_TYPE_AUTHORIZATION,
                                                         status=IPN_PAY_STATUS_ACTIVE,
                                                         approved=True)
        else:
            authorized_list = []
            
        if incomplete:
            incomplete_list = transaction_list.filter(type=PAYMENT_TYPE_AUTHORIZATION,
                                                         status=IPN_PAY_STATUS_INCOMPLETE)
        else:
            incomplete_list = []                      
            
        if completed:
            completed_list = transaction_list.filter(type=PAYMENT_TYPE_AUTHORIZATION,
                                                         status=IPN_PAY_STATUS_COMPLETED)
        else:
            completed_list = []            
        
        if summary:
            pledged_amount = D('0.00')
            authorized_amount = D('0.00')
            incomplete_amount = D('0.00')
            completed_amount = D('0.00')
            
            for t in pledged_list:
                for r in t.receiver_set.all():
                    if r.status == IPN_TXN_STATUS_COMPLETED:
                        # or IPN_SENDER_STATUS_COMPLETED
                        # individual senders may not have been paid due to errors, and disputes/chargebacks only appear here
                        pledged_amount += r.amount
                
            for t in authorized_list:
                authorized_amount += t.amount
                
            for t in incomplete_list:
                incomplete_amount += t.amount
                
            for t in completed_list:
                completed_amount += t.amount                
                
            amount = pledged_amount + authorized_amount + incomplete_amount + completed_amount
            return amount
        
        else:
            return pledged_list | authorized_list | incomplete_list | completed_list   

    def query_user(self, user, summary=False, pledged=True, authorized=True, incomplete=True, completed=True):
        '''
        query_user
        
        Returns either an amount or list of transactions for a user
        
        summary: if true, return a float of the total, if false, return a list of transactions
        pledged: include amounts pledged
        authorized: include amounts pre-authorized
        incomplete: include amounts for transactions with INCOMPLETE status
        completed: include amounts for transactions that are COMPLETED
        
        return value: either a float summary or a list of transactions
        
        '''        
        
        transactions = Transaction.objects.filter(user=user)
        return self.run_query(transactions, summary, pledged, authorized, incomplete=True, completed=True)
       
    def query_campaign(self, campaign, summary=False, pledged=True, authorized=True, incomplete=True, completed=True):
        '''
        query_campaign
        
        Returns either an amount or list of transactions for a campaign
        
        summary: if true, return a float of the total, if false, return a list of transactions
        pledged: include amounts pledged
        authorized: include amounts pre-authorized
        incomplete: include amounts for transactions with INCOMPLETE status
        completed: includes payments that have been completed
        
        return value: either a float summary or a list of transactions
        
        '''        
        
        transactions = Transaction.objects.filter(campaign=campaign)
        return self.run_query(transactions, summary, pledged, authorized, incomplete, completed)
    

    def query_list(self, list, summary=False, pledged=True, authorized=True, incomplete=True, completed=True):
        '''
        query_list
        
        Returns either an amount or list of transactions for a list
        
        summary: if true, return a float of the total, if false, return a list of transactions
        pledged: include amounts pledged
        authorized: include amounts pre-authorized
        incomplete: include amounts for transactions with INCOMPLETE status
        completed: includes payments that have been completed
        
        return value: either a float summary or a list of transactions
        
        '''        
        
        transactions = Transaction.objects.filter(list=list)
        return self.run_query(transactions, summary, pledged, authorized, incomplete, completed)
            
    def execute_campaign(self, campaign):
        '''
        execute_campaign
        
        attempts to execute all pending transactions for a campaign. 
        
        return value: returns a list of transactions with the status of each receiver/transaction updated
        
        '''               
        
        # only allow active transactions to go through again, if there is an error, intervention is needed
        transactions = Transaction.objects.filter(campaign=campaign, status=IPN_PAY_STATUS_ACTIVE)
        
        for t in transactions:
            
            receiver_list = [{'email':settings.PAYPAL_GLUEJAR_EMAIL, 'amount':t.amount}, 
                            {'email':campaign.paypal_receiver, 'amount':D(t.amount) * (D('1.00') - D(str(settings.GLUEJAR_COMMISSION)))}]
            
            self.execute_transaction(t, receiver_list) 

        return transactions

    def finish_campaign(self, campaign):
        '''
        finish_campaign
        
        attempts to execute all remaining payment to non-primary receivers

        
        return value: returns a list of transactions with the status of each receiver/transaction updated
        
        '''               
        
        # QUESTION:  to figure out which transactions are in a state in which the payment to the primary recipient is done but not to secondary recipient
        # Consider two possibilities:  status=IPN_PAY_STATUS_INCOMPLETE or execution = EXECUTE_TYPE_CHAINED_DELAYED
        # which one?  Let's try the second one
        # only allow incomplete transactions to go through again, if there is an error, intervention is needed
        transactions = Transaction.objects.filter(campaign=campaign, execution=EXECUTE_TYPE_CHAINED_DELAYED)
        
        for t in transactions:            
            result = self.finish_transaction(t) 

        return transactions
    
    def cancel_campaign(self, campaign):
        '''
        cancel_campaign
        
        attempts to cancel active preapprovals related to the campaign 

        
        return value: returns a list of transactions with the status of each receiver/transaction updated
        
        '''               
        
        transactions = Transaction.objects.filter(campaign=campaign, status=IPN_PAY_STATUS_ACTIVE)
        
        for t in transactions:            
            result = self.cancel_transaction(t) 

        return transactions    
        

    def finish_transaction(self, transaction):
        '''
        finish_transaction
        
        calls the paypal API to execute payment to non-primary receivers
        
        transaction: the transaction we want to complete
        
        '''
        
        if transaction.execution != EXECUTE_TYPE_CHAINED_DELAYED:
            logger.error("FinishTransaction called with invalid execution type")
            return False
        
        # mark this transaction as executed
        transaction.date_executed = now()
        transaction.save()
        
        p = Execute(transaction)            
        
        # Create a response for this
        envelope = p.envelope()
        
        if envelope:
            correlation = p.correlation_id()
            timestamp = p.timestamp()
        
            r = PaymentResponse.objects.create(api=p.url,
                                              correlation_id = correlation,
                                              timestamp = timestamp,
                                              info = p.raw_response,
                                              transaction=transaction)
        
        if p.success() and not p.error():
            logger.info("finish_transaction Success")
            return True
        
        else:
            transaction.error = p.error_string()
            transaction.save()
            logger.info("finish_transaction error " + p.error_string())
            return False
        
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
        
        # Mark as payment attempted so we will poll this periodically for status changes
        transaction.date_payment = now()
        transaction.save()
        
        p = Pay(transaction)
        
        # Create a response for this
        envelope = p.envelope()
        
        if envelope:
        
            correlation = p.correlation_id()
            timestamp = p.timestamp()
        
            r = PaymentResponse.objects.create(api=p.api(),
                                              correlation_id = correlation,
                                              timestamp = timestamp,
                                              info = p.raw_response,
                                              transaction=transaction)
        
        # We will update our transaction status when we receive the IPN
        if p.success() and not p.error():
            transaction.pay_key = p.key()
            transaction.save()
            logger.info("execute_transaction Success")
            return True
        
        else:
            transaction.error = p.error_string()
            transaction.save()
            logger.info("execute_transaction Error: " + p.error_string())
            return False
    
    def cancel_transaction(self, transaction):
        '''
        cancel
        
        cancels a pre-approved transaction
        
        return value: True if successful, false otherwise
        '''        
        
        p = CancelPreapproval(transaction)
        
        # Create a response for this
        envelope = p.envelope()
        
        if envelope:
        
            correlation = p.correlation_id()
            timestamp = p.timestamp()
        
            r = PaymentResponse.objects.create(api=p.url,
                                              correlation_id = correlation,
                                              timestamp = timestamp,
                                              info = p.raw_response,
                                              transaction=transaction)
        
        if p.success() and not p.error():
            logger.info("Cancel Transaction " + str(transaction.id) + " Completed")
            return True
        
        else:
            transaction.error = p.error_string()
            transaction.save()
            logger.info("Cancel Transaction " + str(transaction.id) + " Failed with error: " + p.error_string())
            return False
        
    def authorize(self, currency, target, amount, expiry=None, campaign=None, list=None, user=None, return_url=None, cancel_url=None, anonymous=False):
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
                                       max_amount=amount,
                                       type=PAYMENT_TYPE_AUTHORIZATION,
                                       execution = EXECUTE_TYPE_CHAINED_DELAYED,
                                       target=target,
                                       currency=currency,
                                       status='NONE',
                                       campaign=campaign,
                                       list=list,
                                       user=user,
                                       anonymous=anonymous
                                       )
        
        # we might want to not allow for a return_url or cancel_url to be passed in but calculated
        # here because we have immediate access to the Transaction object.
        
        if cancel_url is None:
            cancel_path = "{0}?{1}".format(reverse('pledge_cancel'), 
                                urllib.urlencode({'tid':t.id}))            
            cancel_url = urlparse.urljoin(settings.BASE_URL, cancel_path)
            
        if return_url is None:
            return_path = "{0}?{1}".format(reverse('pledge_complete'), 
                                urllib.urlencode({'tid':t.id})) 
            return_url = urlparse.urljoin(settings.BASE_URL, return_path)
        
        p = Preapproval(t, amount, expiry, return_url=return_url, cancel_url=cancel_url)
        
         # Create a response for this
        envelope = p.envelope()
        
        if envelope:        
            r = PaymentResponse.objects.create(api=p.url,
                                              correlation_id = p.correlation_id(),
                                              timestamp = p.timestamp(),
                                              info = p.raw_response,
                                              transaction=t)
        
        if p.success() and not p.error():
            t.preapproval_key = p.key()
            t.save()
            
            url = p.next_url()
                
            logger.info("Authorize Success: " + url)
            return t, url
    
        
        else:
            t.error = p.error_string()
            t.save()
            logger.info("Authorize Error: " + p.error_string())
            return t, None
        
    def modify_transaction(self, transaction, amount=None, expiry=None, return_url=None, cancel_url=None):
        '''
        modify
        
        Modifies a transaction.  The only type of modification allowed is to the amount and expiration date
        
        amount: the new amount
        expiry: the new expiration date, or if none the current expiration date will be used
        return_url: the return URL after the preapproval(if needed)
        cancel_url: the cancel url after the preapproval(if needed)
        
        return value: True if successful, false otherwise.  An optional second parameter for the forward URL if a new authorhization is needed
        '''        
        
        if not amount:
            logger.info("Error, no amount speicified")
            return False
        
        if transaction.type != PAYMENT_TYPE_AUTHORIZATION:
            # Can only modify the amount of a preapproval for now
            logger.info("Error, attempt to modify an invalid transaction type")
            return False, None
        
        if transaction.status != IPN_PAY_STATUS_ACTIVE:
            # Can only modify an active, pending transaction.  If it is completed, we need to do a refund.  If it is incomplete,
            # then an IPN may be pending and we cannot touch it
            logger.info("Error, attempt to modify a transaction that is not active")
            return False, None
            
        if not expiry:
            # Use the old expiration date
            expiry = transaction.date_expired
        
        if amount > transaction.max_amount or expiry != transaction.date_expired:
            
            # Increase or expiration change, cancel and start again
            self.cancel_transaction(transaction)                
                
            # Start a new authorization for the new amount
            
            t, url = self.authorize(transaction.currency, 
                                    transaction.target,
                                    amount,
                                    expiry, 
                                    transaction.campaign, 
                                    transaction.list, 
                                    transaction.user, 
                                    return_url, 
                                    cancel_url, 
                                    transaction.anonymous)
            
            if t and url:
                # Need to re-direct to approve the transaction
                logger.info("New authorization needed, redirectiont to url %s" % url)
                return True, url
            else:
                # No amount change necessary
                logger.info("Error, unable to start a new authorization")
                return False, None
            
        elif amount <= transaction.max_amount:
            # Change the amount but leave the preapproval alone
            transaction.amount = amount
            transaction.save()
            logger.info("Updated amount of transaction to %f" % amount)
            return True, None
        
        else:
            # No changes
            logger.info("Error, no modifications requested")
            return False, None
        
        
    def refund_transaction(self, transaction):
        '''
        refund
        
        Refunds a transaction.  The money for the transaction may have gone to a number of places.   We can only
        refund money that is in our account
        
        return value: True if successful, false otherwise
        '''        
        
        # First check if a payment has been made.  It is possible that some of the receivers may be incomplete
        # We need to verify that the refund API will cancel these
        if transaction.status != IPN_PAY_STATUS_COMPLETED:
            logger.info("Refund Transaction failed, invalid transaction status")
            return False
        
        p = RefundPayment(transaction)
        
        # Create a response for this
        envelope = p.envelope()
        
        if envelope:
        
            correlation = p.correlation_id()
            timestamp = p.timestamp()
        
            r = PaymentResponse.objects.create(api=p.url,
                                              correlation_id = correlation,
                                              timestamp = timestamp,
                                              info = p.raw_response,
                                              transaction=transaction)
        
        if p.success() and not p.error():
            logger.info("Refund Transaction " + str(transaction.id) + " Completed")
            return True
        
        else:
            transaction.error = p.error_string()
            transaction.save()
            logger.info("Refund Transaction " + str(transaction.id) + " Failed with error: " + p.error_string())
            return False
        
    def pledge(self, currency, target, receiver_list, campaign=None, list=None, user=None, return_url=None, cancel_url=None, anonymous=False):
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
                                       max_amount=amount, 
                                       type=PAYMENT_TYPE_INSTANT,
                                       execution=EXECUTE_TYPE_CHAINED_INSTANT,
                                       target=target,
                                       currency=currency,
                                       status='NONE',
                                       campaign=campaign,
                                       list=list,
                                       user=user,
                                       date_payment=now(),
                                       anonymous=anonymous
                                       )
    
        t.create_receivers(receiver_list)
        
        p = Pay(t,return_url=return_url, cancel_url=cancel_url)
        
         # Create a response for this
        envelope = p.envelope()
        logger.info(envelope)
        
        if envelope:        
            r = PaymentResponse.objects.create(api=p.api(),
                                              correlation_id = p.correlation_id(),
                                              timestamp = p.timestamp(),
                                              info = p.raw_response,
                                              transaction=t)
        
        if p.success() and not p.error():
            t.pay_key = p.key()
            t.status = 'CREATED'
            t.save()
            
            if self.embedded:
                url = p.embedded_url()
                logger.info(url)
            else:
                url = p.next_url()
                
            logger.info("Pledge Success: " + url)
            return t, url
        
        else:
            t.error = p.error_string()
            t.save()
            logger.info("Pledge Error: " + p.error_string())
            return t, None
    
    