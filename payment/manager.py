from regluit.core.models import Campaign, Wishlist
from regluit.payment.models import Transaction, Receiver
from django.contrib.auth.models import User
from regluit.payment.parameters import *
from regluit.payment.paypal import Pay, IPN, IPN_TYPE_PAYMENT, IPN_TYPE_PREAPPROVAL, Preapproval
import uuid
import traceback

class PaymentManager( object ): 

    '''
    processIPN
    
    Turns a request from Paypal into an IPN, and extracts info.   We support 2 types of IPNs:
    
    1) Payment - Used for instant payments and to execute pre-approved payments
    2) Preapproval - Used for comfirmation of a preapproval
    
    '''
    def processIPN(self, request):
        
        try:
            ipn = IPN(request)
        
            if ipn.success():
                print "Valid IPN"
    
                
                if ipn.transaction_type == IPN_TYPE_PAYMENT:
                    
                    if ipn.preapproval_key:
                        key = ipn.preapproval_key
                    else:
                        key = ipn.key
                        
                    t = Transaction.objects.get(reference=key)
                    t.status = ipn.status
                    
                    for item in ipn.transactions:
                        
                        r = Receiver.objects.get(transaction=t, email=item['receiver'])
                        r.status = item['status_for_sender_txn']
                        r.save()
                        
                    t.save()
                        
                elif ipn.transaction_type == IPN_TYPE_PREAPPROVAL:
                    
                    t = Transaction.objects.get(reference=ipn.preapproval_key)
                    t.status = ipn.status
                    t.save()
                        
                else:
                    print "IPN: Unknown Transaction Type: " + ipn.transaction_type
                
                
            else:
                print ipn.error
        
        except:
            traceback.print_exc()
        
    '''
    query_campaign
    
    Returns either an amount or list of transactions for a campaign
    
    summary: if true, return a float of the total, if false, return a list of transactions
    pledged: include amounts pledged
    authorized: include amounts pre-authorized
    
    return value: either a float summary or a list of transactions
    
    '''
    def query_campaign(self, campaign, summary=False, pledged=True, authorized=True):
        
        if pledged:
            pledged_list = Transaction.objects.filter(campaign=campaign, 
                                                      type=PAYMENT_TYPE_INSTANT,
                                                      status="COMPLETED")
        else:
            pledged_list = []
        
        if authorized:
            authorized_list = Transaction.objects.filter(campaign=campaign, 
                                                         type=PAYMENT_TYPE_AUTHORIZATION,
                                                         status="ACTIVE")
        else:
            authorized_list = []
        
        if summary:
            pledged_amount = 0.0
            authorized_amount = 0.0
            
            for t in pledged_list:
                pledged_amount += t.amount
                
            for t in authorized_list:
                authorized_amount += t.amount
                
            amount = pledged_amount + authorized_amount
            return amount
        
        else:
            return pledged_list | authorized_list
            
    '''
    execute_campaign
    
    attempts to execute all pending transactions for a campaign. 
    
    return value: returns a list of transactions with the status of each receiver/transaction updated
    
    '''       
    def execute_campaign(self, campaign):
        
        transactions = Transaction.objects.filter(campaign=campaign, status="ACTIVE")
        
        for t in transactions:
            
            receiver_list = [{'email':'jakace_1309677337_biz@gmail.com', 'amount':t.amount * 0.80}, 
                            {'email':'boogus@gmail.com', 'amount':t.amount * 0.20}]
            
            self.execute_transaction(t, receiver_list) 

        return transactions
    
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
    def execute_transaction(self, transaction, receiver_list):
        
        for r in receiver_list:
            receiver = Receiver.objects.create(email=r['email'], amount=r['amount'], currency=transaction.currency, status="ACTIVE", transaction=transaction)
        
        p = Pay(transaction, receiver_list)
        transaction.status = p.status()
        
        if p.status() == 'COMPLETED':
            print "Execute Success"
            return True
        
        else:
            transaction.error = p.error()
            print "Execute Error: " + p.error()
            return False
        
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
    def authorize(self, currency, target, amount, campaign=None, list=None, user=None):
            
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
        
        p = Preapproval(t, amount)
        
        if p.status() == 'Success':
            t.status = 'CREATED'
            t.reference = p.paykey()
            t.save()
            print "Authorize Success: " + p.next_url()
            return t, p.next_url()
        
        else:
            t.status = 'ERROR'
            t.error = p.error()
            t.save()
            print "Authorize Error: " + p.error()
            return t, None
        
    
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
    def pledge(self, currency, target, receiver_list, campaign=None, list=None, user=None):
        
        amount = 0.0
        for r in receiver_list:
            amount += r['amount']
            
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
    
        for r in receiver_list:
            receiver = Receiver.objects.create(email=r['email'], amount=r['amount'], currency=currency, status="None", transaction=t)
        
        p = Pay(t, receiver_list)
        t.status = p.status()
        
        if p.status() == 'CREATED':
            t.reference = p.paykey()
            t.save()
            print "Pledge Success: " + p.next_url()
            return t, p.next_url()
        
        else:
            t.error = p.error()
            t.save()
            print "Pledge Status: " + p.status() +  "Error: " + p.error()
            return t, None
    
    