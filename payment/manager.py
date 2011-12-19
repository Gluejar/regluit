from regluit.core.models import Campaign, Wishlist
from regluit.payment.models import Transaction, Receiver, PaymentResponse
from django.contrib.auth.models import User
from regluit.payment.parameters import *
from regluit.payment.paypal import Pay, Execute, IPN, IPN_TYPE_PAYMENT, IPN_TYPE_PREAPPROVAL, IPN_TYPE_ADJUSTMENT, Preapproval, IPN_PAY_STATUS_COMPLETED, CancelPreapproval, PaymentDetails, PreapprovalDetails, IPN_SENDER_STATUS_COMPLETED, IPN_TXN_STATUS_COMPLETED
import uuid
import traceback
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging
from decimal import Decimal as D
from xml.dom import minidom

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

    def checkStatus(self, past_days=3):
        
        '''
        Run through all pay transactions and verify that their current status is as we think.
        '''
        
        doc = minidom.Document()
        head = doc.createElement('transactions')
        doc.appendChild(head)
        
        # look at all transacitons for stated number of past days; if past_days is not int, get all Transaction
        try:
            ref_date = datetime.now() - relativedelta(days=int(past_days))
            transactions = Transaction.objects.filter(date_payment__gte=ref_date)
        except:
            ref_date = datetime.now()
            transactions = Transaction.objects.filter(date_payment__isnull=False)
            
        logger.info(transactions)
        
        for t in transactions:
        
            tran = doc.createElement('transaction')
            tran.setAttribute("id", str(t.id))
            head.appendChild(tran)
                
            p = PaymentDetails(t)
            
            if p.error() or not p.success():
                logger.info("Error retrieving payment details for transaction %d" % t.id)
                append_element(doc, tran, "error", "An error occurred while verifying this transaction, see server logs for details")
                
            else:
                
                # Check the transaction status
                if t.status != p.status:
                    append_element(doc, tran, "status_ours", t.status)
                    append_element(doc, tran, "status_theirs", p.status)
                    t.status = p.status
                    t.save()
                
                for r in p.transactions:
                    
                    try:
                        receiver = Receiver.objects.get(transaction=t, email=r['email'])
                        logger.info(r)
                        logger.info(receiver)
                        
                        # Check for updates on each receiver's status.  Note that unprocessed delayed chained payments
                        # will not have a status code or txn id code
                        if receiver.status != r['status']:
                            append_element(doc, tran, "receiver_status_ours", receiver.status)
                            append_element(doc, tran, "receiver_status_theirs", r['status'])
                            receiver.status = r['status']
                            receiver.save()
                            
                        if receiver.txn_id != r['txn_id']:
                            append_element(doc, tran, "txn_id_ours", receiver.txn_id)
                            append_element(doc, tran, "txn_id_theirs", r['txn_id'])
                            receiver.txn_id = r['txn_id']
                            receiver.save()
                            
                    except:
                        traceback.print_exc()
                        
        # Now look for preapprovals that have not been paid and check on their status
        transactions = Transaction.objects.filter(date_authorized__gte=ref_date, date_payment=None, type=PAYMENT_TYPE_AUTHORIZATION)
        
        for t in transactions:
            
            p = PreapprovalDetails(t)
            
            tran = doc.createElement('preapproval')
            tran.setAttribute("key", str(t.preapproval_key))
            head.appendChild(tran)
            
            if p.error() or not p.success():
                logger.info("Error retrieving preapproval details for transaction %d" % t.id)
                append_element(doc, tran, "error", "An error occurred while verifying this transaction, see server logs for details")
                
            else:
                
                # Check the transaction status
                if t.status != p.status:
                    append_element(doc, tran, "status_ours", t.status)
                    append_element(doc, tran, "status_theirs", p.status)
                    t.status = p.status
                    t.save()
                    
                # check the currency code
                if t.currency != p.currency:
                    append_element(doc, tran, "currency_ours", t.currency)
                    append_element(doc, tran, "currency_theirs", p.currency)
                    t.currency = p.currency
                    t.save()
                    
                # Check the amount
                if t.amount != D(p.amount):
                    append_element(doc, tran, "amount_ours", str(t.amount))
                    append_element(doc, tran, "amount_theirs", str(p.amount))
                    t.amount = p.amount
                    t.save()
                            

        return doc.toxml()
    
        
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
                    
                        
                elif ipn.transaction_type == IPN_TYPE_PREAPPROVAL:
                    
                    # IPN for preapproval always uses the key to ref the transaction as this is always valid
                    key = ipn.preapproval_key
                    t = Transaction.objects.get(preapproval_key=key)
                    
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
            # Campaign.paypal_receiver
            receiver_list = [{'email':settings.PAYPAL_GLUEJAR_EMAIL, 'amount':t.amount}, 
                            {'email':campaign.paypal_receiver, 'amount':D(t.amount) * (D('1.00') - D(str(settings.GLUEJAR_COMMISSION)))}]
            
            self.execute_transaction(t, receiver_list) 

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
        transaction.date_executed = datetime.now()
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
        transaction.date_payment = datetime.now()
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
    
    def cancel(self, transaction):
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
        
    def authorize(self, currency, target, amount, campaign=None, list=None, user=None, return_url=None, cancel_url=None, anonymous=False):
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
                                       execution = EXECUTE_TYPE_CHAINED_DELAYED,
                                       target=target,
                                       currency=currency,
                                       status='NONE',
                                       campaign=campaign,
                                       list=list,
                                       user=user,
                                       anonymous=anonymous
                                       )
        
        p = Preapproval(t, amount, return_url=return_url, cancel_url=cancel_url)
        
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
                                       type=PAYMENT_TYPE_INSTANT,
                                       execution=EXECUTE_TYPE_CHAINED_INSTANT,
                                       target=target,
                                       currency=currency,
                                       status='NONE',
                                       campaign=campaign,
                                       list=list,
                                       user=user,
                                       date_payment=datetime.now(),
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
    
    