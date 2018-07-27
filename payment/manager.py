"""
external library imports
"""
import logging
import traceback
import urllib
import urlparse
import uuid

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal as D
from xml.dom import minidom

"""
django imports
"""
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.timezone import now

"""
regluit imports
"""
from regluit.payment import credit
from regluit.payment.models import Transaction, Receiver, PaymentResponse, Account
from regluit.payment.parameters import *
from regluit.payment.signals import transaction_charged, pledge_modified, pledge_created

logger = logging.getLogger(__name__)

def append_element(doc, parent, name, text):
    
    element = doc.createElement(name)
    parent.appendChild(element)
    text_node = doc.createTextNode(text)
    element.appendChild(text_node)
    
    return element

# at this point, there is no internal context and therefore, the methods of PaymentManager can be recast into static methods
class PaymentManager( object ): 
            
    def processIPN(self, request, module):
        
        # Forward to our payment processor
        mod = __import__("regluit.payment." + module, fromlist=[str(module)])
        return mod.Processor().ProcessIPN(request)

    def update_preapproval(self, transaction):
        """Update a transaction to hold the data from a PreapprovalDetails on that transaction"""
        t = transaction
        p = transaction.get_payment_class().PreapprovalDetails(t)
                    
        preapproval_status = {'id':t.id, 'key':t.preapproval_key}
        
        if p.error() or not p.success():
            logger.info("Error retrieving preapproval details for transaction %d" % t.id)
            preapproval_status["error"] = "An error occurred while verifying this transaction, see server logs for details"
        else:
            
            # Check the transaction status
            if t.status != p.status:
                preapproval_status["status"] = {'ours':t.status, 'theirs':p.status}
                t.status = p.status
                t.local_status = p.local_status
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
                
            # In amazon FPS, we may not have a pay_key via the return URL, update here
            try:
                if t.pay_key != p.pay_key:
                    preapproval_status['pay_key'] = {'ours':t.pay_key, 'theirs':p.pay_key}
                    t.pay_key = p.pay_key
                    t.save()
            except:
                # No problem, p.pay_key is not defined for paypal function
                blah = "blah"
            
        
        return preapproval_status            

    def update_payment(self, transaction):
        """Update a transaction to hold the data from a PaymentDetails on that transaction"""
        t = transaction
        payment_status = {'id':t.id}
            
        p = transaction.get_payment_class().PaymentDetails(t)
        
        if p.error() or not p.success():
            logger.info("Error retrieving payment details for transaction %d" % t.id)
            payment_status['error'] = "An error occurred while verifying this transaction, see server logs for details"
        else:
            
            # Check the transaction status
            if t.status != p.status:
                payment_status['status'] = {'ours': t.status, 'theirs': p.status}
                
                t.status = p.status
                t.local_status = p.local_status
                t.save()
                
            receivers_status = []
            
            for r in p.transactions:
                # This is only supported for paypal at this time
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
            
            # deal with preapprovals
            if t.date_payment is None:
                preapproval_status = self.update_preapproval(t)
                logger.info("transaction: {0}, preapproval_status: {1}".format(t, preapproval_status))
                if not set(['status', 'currency', 'amount', 'approved']).isdisjoint(set(preapproval_status.keys())):
                    status["preapprovals"].append(preapproval_status)
            # update payments
            else:
                payment_status = self.update_payment(t)
                if not set(["status", "receivers"]).isdisjoint(payment_status.keys()):
                    status["payments"].append(payment_status)
                    
        # Clear out older, duplicate preapproval transactions
        cleared_list = []
        for p in transactions:
            
            # pick out only the preapprovals
            if p.date_payment is None and p.type == PAYMENT_TYPE_AUTHORIZATION and p.status == TRANSACTION_STATUS_ACTIVE and p not in cleared_list:
                
                # keep only the newest transaction for this user and campaign                
                user_transactions_for_campaign = Transaction.objects.filter(user=p.user, status=TRANSACTION_STATUS_ACTIVE, campaign=p.campaign).order_by('-date_authorized')
                
                if len(user_transactions_for_campaign) > 1:
                    logger.info("Found %d active transactions for campaign" % len(user_transactions_for_campaign))
                    self.cancel_related_transaction(user_transactions_for_campaign[0], status=TRANSACTION_STATUS_ACTIVE, campaign=transactions[0].campaign)
                    
                cleared_list.extend(user_transactions_for_campaign)
                    
            # Note, we may need to call checkstatus again here
            
        return status
    
         
    def run_query(self, transaction_list, summary=True, campaign_total=False, pledged=False, authorized=False, incomplete=False, completed=False, pending=False, error=False, failed=False, **kwargs):
        '''
        Generic query handler for returning summary and transaction info,  see query_user and query_campaign
        
        campaign_total=True includes all payment types which should count towards campaign total
        
        '''
        if campaign_total:
            # must double check when adding Paypal or other
            # return only ACTIVE transactions with approved=True
            list = transaction_list.filter(type=PAYMENT_TYPE_AUTHORIZATION,
                                                approved=True).exclude(status=TRANSACTION_STATUS_CANCELED)
            list = list | transaction_list.filter(type=PAYMENT_TYPE_INSTANT,
                                                   status=TRANSACTION_STATUS_COMPLETE)
        else:                                       
            list = Transaction.objects.none()
            if pledged:
                list = list | transaction_list.filter(type=PAYMENT_TYPE_INSTANT,
                                                       status=TRANSACTION_STATUS_COMPLETE)
            
            if authorized:
                # return only ACTIVE transactions with approved=True
                list = list | transaction_list.filter(type=PAYMENT_TYPE_AUTHORIZATION,
                                                             status=TRANSACTION_STATUS_ACTIVE,
                                                             approved=True)                
            if incomplete:
                list = list | transaction_list.filter(type=PAYMENT_TYPE_AUTHORIZATION,
                                                             status=TRANSACTION_STATUS_INCOMPLETE)
            if completed:
                list = list | transaction_list.filter(type=PAYMENT_TYPE_AUTHORIZATION,
                                                             status=TRANSACTION_STATUS_COMPLETE)        
            if pending:
                list = list | transaction_list.filter(type=PAYMENT_TYPE_AUTHORIZATION,
                                                             status=TRANSACTION_STATUS_PENDING)        
            if error:
                list = list | transaction_list.filter(type=PAYMENT_TYPE_AUTHORIZATION,
                                                             status=TRANSACTION_STATUS_ERROR)        
            if failed:
                list = list | transaction_list.filter(type=PAYMENT_TYPE_AUTHORIZATION,
                                                             status=TRANSACTION_STATUS_FAILED)        
        if summary:
            amount = D('0.00')
            for t in list:
                amount += t.amount
            return amount
        
        else:
            return list   

    def query_user(self, user,  **kwargs):
        '''
        query_user
        
        Returns either an amount or list of transactions for a user
        
        summary: if true, return a float of the total, if false, return a list of transactions
        
        return value: either a float summary or a list of transactions
        Note: this method appears to be unused.
        
        '''        
        
        transactions = Transaction.objects.filter(user=user)
        return self.run_query(transactions,  **kwargs)
       
    def query_campaign(self, campaign, **kwargs ):
        '''
        query_campaign
        
        Returns either an amount or list of transactions for a campaign
        
        summary: if true, return a float of the total, if false, return a list of transactions
        
        return value: either a float summary or a list of transactions
                
        '''        
        
        transactions = Transaction.objects.filter(campaign=campaign)
        return self.run_query(transactions, **kwargs)
    

            
    def execute_campaign(self, campaign):
        '''
        execute_campaign
        
        attempts to execute all pending transactions for a campaign. 
        
        return value: returns a list of transactions with the status of each receiver/transaction updated
        
        '''               
        
        # only allow active transactions to go through again, if there is an error, intervention is needed
        transactions = Transaction.objects.filter(campaign=campaign, status=TRANSACTION_STATUS_ACTIVE)

        results = []
        
        for t in transactions:
            # 
            # Currently receivers are only used for paypal, so it is OK to leave the paypal info here
            #
            receiver_list = [{'email':settings.PAYPAL_GLUEJAR_EMAIL, 'amount':t.amount}, 
                            {'email':campaign.paypal_receiver, 'amount':D(t.amount) * (D('1.00') - D(str(settings.GLUEJAR_COMMISSION)))}]
            
            try:
                self.execute_transaction(t, receiver_list)
            except Exception as e:
                results.append((t, e))
            else:
                results.append((t, None))

        return results

    def finish_campaign(self, campaign):
        '''
        finish_campaign
        
        attempts to execute all remaining payment to non-primary receivers

        This is currently only supported for paypal
        
        return value: returns a list of transactions with the status of each receiver/transaction updated
        
        '''               
        
        # QUESTION:  to figure out which transactions are in a state in which the payment to the primary recipient is done but not to secondary recipient
        # Consider two possibilities:  status=IPN_PAY_STATUS_INCOMPLETE or execution = EXECUTE_TYPE_CHAINED_DELAYED
        # which one?  Let's try the second one
        # only allow incomplete transactions to go through again, if there is an error, intervention is needed
        transactions = Transaction.objects.filter(campaign=campaign, execution=EXECUTE_TYPE_CHAINED_DELAYED)
        
        for t in transactions:            
            result = self.finish_transaction(t) 

        # TO DO:  update campaign status
        
        
        return transactions
    
    def cancel_campaign(self, campaign, reason="UNSUCCESSFUL CAMPAIGN"):
        '''
        cancel_campaign
        
        attempts to cancel active preapprovals related to the campaign 

        
        return value: returns a list of transactions with the status of each receiver/transaction updated
        
        '''               
        
        transactions = Transaction.objects.filter(campaign=campaign, status=TRANSACTION_STATUS_ACTIVE)
        
        for t in transactions:            
            result = self.cancel_transaction(t)
            if result:
                t.reason = reason
                t.save()

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
        
        p = transaction.get_payment_class().Finish(transaction)            
        
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
        transaction.set_payment()
        
        p = transaction.get_payment_class().Execute(transaction)
        
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
            return True
        
        else:
            transaction.error = p.error_string()
            transaction.save()
            logger.info("execute_transaction Error: {}".format(p.error_string()))
            return False
    
    def cancel_transaction(self, transaction):
        '''
        cancel
        
        cancels a pre-approved transaction
        
        return value: True if successful, false otherwise
        '''        
        
        # does this transaction explicity require preapprovals?
        requires_explicit_preapprovals = transaction.get_payment_class().requires_explicit_preapprovals
        
        if requires_explicit_preapprovals:
                
            p = transaction.get_payment_class().CancelPreapproval(transaction) 
            
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
                logger.info("Cancel Transaction {} Failed with error: {}".format(transaction.id, p.error_string()))
                return False
            
        else:
            
        # if no explicit preapproval required, we just have to mark the transaction as cancelled.
            transaction.status = TRANSACTION_STATUS_CANCELED
            transaction.save()
            return True
        
    def authorize(self, transaction, expiry= None, return_url=None,  paymentReason="unglue.it Pledge", modification=False):
        '''
        authorize
        
        authorizes a set amount of money to be collected at a later date
        
        return_url: url to redirect supporter to after a successful transaction
        paymentReason:  a memo line that will show up in the unglue.it accounting
        modification: whether this authorize call is part of a modification of an existing pledge
        
        return value: a tuple of the new transaction object and a re-direct url.  If the process fails,
                      the redirect url will be None
                      
        '''    
        
        if transaction.host == PAYMENT_HOST_NONE:
            #TODO send user to select a payment processor -- for now, set to a system setting
            transaction.host = settings.PAYMENT_PROCESSOR    
                
        # we might want to not allow for a return_url  to be passed in but calculated
        # here because we have immediate access to the Transaction object.
        
            
        if return_url is None:
            return_path = "{0}?{1}".format(reverse('pledge_complete'), 
                                urllib.urlencode({'tid':transaction.id})) 
            return_url = urlparse.urljoin(settings.BASE_URL_SECURE, return_path)
        
        p = transaction.get_payment_class().Preapproval(transaction, transaction.max_amount, expiry, return_url=return_url, paymentReason=paymentReason) 
       
         # Create a response for this
        envelope = p.envelope()
        
        if envelope:        
            r = PaymentResponse.objects.create(api=p.url,
                                              correlation_id = p.correlation_id(),
                                              timestamp = p.timestamp(),
                                              info = p.raw_response,
                                              transaction=transaction)
        
        if p.success() and not p.error():
            transaction.preapproval_key = p.key()
            transaction.save()
            
            # it make sense for the payment processor library to calculate next_url when
            # user is redirected there.  But if no redirection is required, send user
            # straight on to the return_url
            url = p.next_url()
            
            if url is None:
                url = return_url
                
            logger.info("Authorize Success: " + url if url is not None else '')
            
            # modification and initial pledge use different notification templates --
            # decide which to send
            # we need to fire notifications at the first point at which we are sure
            # that the transaction has successfully completed; triggering notifications
            # when the transaction is initiated risks sending notifications on transactions
            # that for whatever reason fail.  will need other housekeeping to handle those.
            # sadly this point is not yet late enough in the process -- needs to be moved
            # until after we are certain.
            
            if not modification:
                # BUGBUG: 
                # send the notice here for now
                # this is actually premature since we're only about to send the user off to the payment system to
                # authorize a charge
                pledge_created.send(sender=self, transaction=transaction)
                
            return transaction, url
    
        
        else:
            transaction.error = p.error_string()
            transaction.save()
            logger.info("Authorize Error: " + p.error_string())
            return transaction, None

    def charge(self, transaction,  return_url=None,  paymentReason="unglue.it Purchase", token = None):
        '''
        charge
        
        immediately attempt to collect on transaction 
        
        return_url: url to redirect supporter to after a successful transaction
        paymentReason:  a memo line that will show up in our stripe accounting
        
        return value: a tuple of the new transaction object and a re-direct url.  If the process fails,
                      the redirect url will be None
                      
        '''

        if transaction.host == PAYMENT_HOST_NONE:
            #TODO send user to select a payment processor -- for now, set to a system setting
            transaction.host = settings.PAYMENT_PROCESSOR 
                
        # we might want to not allow for a return_url to be passed in but calculated
        # here because we have immediate access to the Transaction object.
        charge_amount = transaction.needed_amount
        if transaction.credit_amount > 0 :
            success = credit.pay_transaction(transaction, transaction.user, transaction.campaign.user_to_pay, transaction.credit_amount)
            if not success:  #shouldn't happen
                logger.error('could not use credit for transaction %s' % transaction.id)
                charge_amount =transaction.max_amount
        p = transaction.get_payment_class().Pay(transaction, amount=charge_amount, return_url=return_url, paymentReason=paymentReason, token=token)
       
        
        if p.success() and not p.error():
            transaction.preapproval_key = p.key()
            transaction.execution = EXECUTE_TYPE_INSTANT
            transaction.set_executed() # also does the save
            
            # it make sense for the payment processor library to calculate next_url when
            # user is redirected there.  But if no redirection is required, send user
            # straight on to the return_url
            url = p.next_url()
            
            if url is None:
                url = return_url
                
            logger.info("Pay Success: " + url if url is not None else '')
                            
            return transaction, url
    
        
        else:
            transaction.error = p.error_string()
            transaction.save()
            logger.info("Pay Error: {}".format(p.error_string()))
            return transaction, None


            
    def process_transaction(self, currency,  amount, host=PAYMENT_HOST_NONE, campaign=None, 
         user=None, return_url=None, paymentReason="unglue.it Pledge",  pledge_extra=None,
         donation=False, modification=False):
        '''
        process
        
        saves and processes a proposed transaction; decides if the transaction should be processed 
        immediately.
        
        currency: a 3-letter currency code, i.e. USD
        amount: the amount to authorize
        host: the name of the processing module; if none, send user back to decide!
        campaign: required campaign object
        user: optional user object
        return_url: url to redirect supporter to after a successful transaction
        paymentReason:  a memo line that will show up in the Payer's Amazon (and Paypal?) account
        modification: whether this authorize call is part of a modification of an existing pledge
        pledge_extra: extra pledge stuff
        
        return value: a tuple of the new transaction object and a re-direct url.  
                      If the process fails, the redirect url will be None
        donation: transaction is a donation
        '''    
        # set the expiry date based on the campaign deadline
        if campaign and campaign.deadline:
            expiry = campaign.deadline + timedelta(days=settings.PREAPPROVAL_PERIOD_AFTER_CAMPAIGN)
        else:
            expiry = now() + timedelta(days=settings.PREAPPROVAL_PERIOD_AFTER_CAMPAIGN)

        t = Transaction.create(
                amount=0,
                host = host,
                max_amount=amount,
                currency=currency,
                campaign=campaign,
                user=user,
                pledge_extra=pledge_extra,
                donation=donation,
        )
        t.save()
        # does user have enough credit to transact now?
        if user.is_authenticated and user.credit.available >= amount :
            # YES!
            return_path = "{0}?{1}".format(reverse('pledge_complete'), 
                                urllib.urlencode({'tid':t.id})) 
            return_url = urlparse.urljoin(settings.BASE_URL_SECURE, return_path)
            if campaign.is_pledge() :
                success = credit.pledge_transaction(t,user,amount)
                if success:
                    pledge_created.send(sender=self, transaction=t)
            else:
                success = credit.pay_transaction(t,user,t.campaign.user_to_pay, amount)
                if success:
                    t.amount = amount
                    t.host = PAYMENT_HOST_CREDIT
                    t.execution = EXECUTE_TYPE_INSTANT
                    t.date_executed = now()
                    t.status = TRANSACTION_STATUS_COMPLETE
                    t.save()
                    transaction_charged.send(sender=self, transaction=t)
            if success:
                return t, return_url
            else:
                # shouldn't happen
                logger.error('could not use credit for transaction %s' % t.id)
            
                
        # send user to choose payment path
        return t, reverse('fund', args=[t.id])

        
    def cancel_related_transaction(self, transaction, status=TRANSACTION_STATUS_ACTIVE, campaign=None):
        '''
        Cancels any other similar status transactions for the same campaign.  Used with modify code
        
        Returns the number of transactions successfully canceled
        '''
        
        related_transactions = Transaction.objects.filter(status=status, user=transaction.user)
        
        if len(related_transactions) == 0:
            return 0
        
        if campaign:
            related_transactions = related_transactions.filter(campaign=campaign)
            
        canceled = 0
        
        for t in related_transactions:
            
            if t.id == transaction.id:
                # keep our transaction
                continue
            
            if self.cancel_transaction(t): 
                canceled = canceled + 1
                # send notice about modification of transaction
                if transaction.amount > t.amount:
                    # this should be the only one that happens
                    up_or_down = "increased"
                elif transaction.amount < t.amount:
                    # we shouldn't expect any case in which this happens
                    up_or_down = "decreased"
                else:
                    # we shouldn't expect any case in which this happens
                    up_or_down = None
                    
                pledge_modified.send(sender=self, transaction=transaction, up_or_down=up_or_down)
            else:
                logger.error("Failed to cancel transaction {0} for related transaction {1} ".format(t, transaction))
            
        return canceled
    
    def modify_transaction(self, transaction, amount, expiry=None, pledge_extra=None,
                           return_url=None, nevermind_url=None, paymentReason=None):
        '''
        modify
        
        Modifies a transaction.  
        2 main situations:  if the new amount is less than max_amount, no need to go out to Stripe again
        if new amount is greater than max_amount...need to go out and get new approval.
        to start with, we can use the standard pledge_complete, pledge_cancel machinery
        might have to modify the pledge_complete, pledge_cancel because the messages are going to be
        different because we're modifying a pledge rather than a new one.
        
        amount: the new amount
        expiry: the new expiration date, or if none the current expiration date will be used
        return_url: the return URL after the preapproval(if needed)
        paymentReason: a memo line that will show up in the Payer's Amazon (and Paypal?) account
        
        return value: True if successful, False otherwise.  An optional second parameter for the forward URL if a new authorhization is needed
        '''
        
        logger.info("transaction.id: {0}, amount:{1}".format(transaction.id, amount))
        if amount < transaction.amount:
            up_or_down = "decreased"
        elif amount > transaction.amount:
            up_or_down =  "increased"
        else:
            up_or_down =  "modified"


        # if expiry is None, use the existing value          
        if expiry is None:
            expiry = transaction.date_expired
            
        # does this transaction explicity require preapprovals?
        
        requires_explicit_preapprovals = transaction.get_payment_class().requires_explicit_preapprovals
        
        if transaction.type != PAYMENT_TYPE_AUTHORIZATION:
            logger.info("Error, attempt to modify an invalid transaction type")
            return False, None
        
        # Can only modify an active, pending transaction.  If it is completed, we need to do a refund.  If it is incomplete,
        # then an IPN may be pending and we cannot touch it        
        if transaction.status != TRANSACTION_STATUS_ACTIVE:
            logger.info("Error, attempt to modify a transaction that is not active")
            return False, None
            
        if transaction.host == PAYMENT_HOST_CREDIT:
            # does user have enough credit to pledge now?
            if transaction.user.credit.available >= amount-transaction.amount :
                # YES!
                transaction.set_pledge_extra(pledge_extra)
                credit.pledge_transaction(transaction,transaction.user,amount)
                return_path = "{0}?{1}".format(reverse('pledge_complete'), 
                                    urllib.urlencode({'tid':transaction.id})) 
                return_url = urlparse.urljoin(settings.BASE_URL_SECURE, return_path)
                
                logger.info("Updated amount of transaction to %f" % amount)
                pledge_modified.send(sender=self, transaction=transaction,up_or_down=up_or_down)
                return transaction, return_url
            else:
                # cancel old transaction, send user to choose new payment path
                # set the expiry date based on the campaign deadline
                expiry = transaction.deadline_or_now + timedelta( days=settings.PREAPPROVAL_PERIOD_AFTER_CAMPAIGN )
                t = Transaction.create(amount=0, 
                           max_amount=amount,
                           currency=transaction.currency,
                           status=TRANSACTION_STATUS_MODIFIED,
                           campaign=transaction.campaign,
                           user=transaction.user,
                           pledge_extra=pledge_extra
                           )
                t.save()
                credit.Processor.CancelPreapproval(transaction)
                return t, reverse('fund_%s'%campaign.type, args=[t.id])

        elif requires_explicit_preapprovals and (amount > transaction.max_amount or expiry != transaction.date_expired):

            # set the expiry date based on the campaign deadline
            expiry = transaction.deadline_or_now + timedelta( days=settings.PREAPPROVAL_PERIOD_AFTER_CAMPAIGN )
                
            # Start a new transaction for the new amount
            t = Transaction.create(amount=amount, 
                                       max_amount=amount,
                                       host=transaction.host,
                                       currency=transaction.currency,
                                       status=TRANSACTION_STATUS_CREATED,
                                       campaign=transaction.campaign,
                                       user=transaction.user,
                                       pledge_extra=pledge_extra
                                       )
            t.save()
            t, url = self.authorize(transaction,
                                    expiry=expiry if expiry else transaction.date_expired, 
                                    return_url=return_url, 
                                    paymentReason=paymentReason,
                                    modification=True
                                    )
            
            if t and url:
                # Need to re-direct to approve the transaction
                logger.info("New authorization needed, redirection to url %s" % url)
                
                # Do not cancel the transaction here, wait until we get confirmation that the transaction is complete
                # then cancel all other active transactions for this campaign
                #self.cancel_transaction(transaction)    

                # while it would seem to make sense to send a pledge notification change here
                # if we do, we will also send notifications when we initiate but do not
                # successfully complete a pledge modification

                return True, url
            else:
                # a problem in authorize
                logger.info("Error, unable to start a new authorization")
                # should we send a pledge_modified signal with state="failed" and a
                # corresponding notification to the user? that would go here.
                return False, None
            
        elif (requires_explicit_preapprovals and amount <= transaction.max_amount) or (not requires_explicit_preapprovals):
            # Update transaction but leave the preapproval alone
            transaction.amount = amount
            transaction.set_pledge_extra(pledge_extra)
            
            transaction.save()
            logger.info("Updated amount of transaction to %f" % amount)
            # when modifying pledges happens immediately and only within our
            # db, we don't have to wait until we hear back to be assured of
            # success; send the notification immediately
            pledge_modified.send(sender=self, transaction=transaction, up_or_down=up_or_down)
            return True, None
        else:
            # this shouldn't happen
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
        if transaction.status != TRANSACTION_STATUS_COMPLETE:
            logger.info("Refund Transaction failed, invalid transaction status")
            return False
        
        p = transaction.get_payment_class().RefundPayment(transaction) 
        
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
            logger.info("Refund Transaction {}  Failed with error:  {}".format(str(transaction.id), p.error_string()))
            return False
        
    def make_account(self, user=None, host=None, token=None):
        """delegate to a specific payment module the task of creating a payment account"""
        
        mod = __import__("regluit.payment." + host, fromlist=[host])
        return mod.Processor().make_account(user=user, token=token)
        
    def retrieve_accounts(self, user, host, include_deactivated=False):
        """return any accounts that match user, host -- only active ones by default"""
        
        if include_deactivated:
            return Account.objects.filter(user=user, host=host)
        else:
            return Account.objects.filter(user=user, host=host, date_deactivated__isnull=True)

    
