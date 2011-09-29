from regluit.core.models import Campaign, Wishlist
from regluit.payment.models import Transaction, Receiver
from django.contrib.auth.models import User
from regluit.payment.parameters import *
from regluit.payment.paypal import Pay, IPN, IPN_TYPE_PAYMENT
import uuid
import traceback

class PaymentManager( object ): 

    
    def processIPN(self, request):
        
        try:
            ipn = IPN(request)
        
            if ipn.success():
                print "Valid IPN"
            
                t = Transaction.objects.get(reference=ipn.key)
                
                if ipn.transaction_type == IPN_TYPE_PAYMENT:
                    
                    t.status = ipn.status
                    
                    for item in ipn.transactions:
                        
                        r = Receiver.objects.get(transaction=t, email=item['receiver'])
                        r.status = item['status_for_sender_txn']
                        r.save()
                        
                else:
                    print "IPN: Unknown Transaction Type: " + ipn.transaction_type
                
                t.save()
            else:
                print ipn.error
        
        except:
            traceback.print_exc()
        
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
                                                         status="PENDING")
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
            
        
    def pledge(self, currency, target, receiver_list, campaign=None, list=None, user=None):
        
        self.currency = currency
        amount = 0.0
        for r in receiver_list:
            amount += r['amount']
            
        t = Transaction.objects.create(amount=amount, 
                                       type=PAYMENT_TYPE_INSTANT, 
                                       target=target,
                                       currency=self.currency,
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
            t.reference = p.error()
            t.save()
            print "Pledge Error: " + p.error()
            return t, None
    
    