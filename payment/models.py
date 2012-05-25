from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from regluit.core.models import Campaign, Wishlist, Premium
from regluit.payment.parameters import *
from decimal import Decimal
import uuid

    
class Transaction(models.Model):
    
    # type e.g., PAYMENT_TYPE_INSTANT or PAYMENT_TYPE_AUTHORIZATION -- defined in parameters.py
    type = models.IntegerField(default=PAYMENT_TYPE_NONE, null=False)
    
    # host: the payment processor.  Named after the payment module that hosts the payment processing functions
    host = models.CharField(default=settings.PAYMENT_PROCESSOR, max_length=32, null=False)
    
    # target: e.g, TARGET_TYPE_CAMPAIGN,  TARGET_TYPE_LIST -- defined in parameters.py 
    target = models.IntegerField(default=TARGET_TYPE_NONE, null=False)
    
    #execution: e.g. EXECUTE_TYPE_CHAINED_INSTANT, EXECUTE_TYPE_CHAINED_DELAYED, EXECUTE_TYPE_PARALLEL
    execution = models.IntegerField(default=EXECUTE_TYPE_NONE, null=False)
    
    # status: general status constants defined in parameters.py
    status = models.CharField(max_length=32, default='None', null=False)
    
    # local_status: status code specific to the payment processor
    local_status = models.CharField(max_length=32, default='NONE', null=True)
    
    # amount & currency -- amount of money and its currency involved for transaction
    amount = models.DecimalField(default=Decimal('0.00'), max_digits=14, decimal_places=2) # max 999,999,999,999.99
    max_amount = models.DecimalField(default=Decimal('0.00'), max_digits=14, decimal_places=2) # max 999,999,999,999.99
    currency = models.CharField(max_length=10, default='USD', null=True)
    
    # a unique ID that can be passed to PayPal to track a transaction
    secret = models.CharField(max_length=64, null=True)
    
    # a paykey that PayPal generates to identify this transaction
    pay_key = models.CharField(max_length=128, null=True)
    
    # a preapproval key that Paypal generates to identify this transaction
    preapproval_key = models.CharField(max_length=128, null=True)
    
    # (RY is not sure what receipt is for)
    receipt = models.CharField(max_length=256, null=True)
    
    # whether a Preapproval has been approved or not
    approved = models.NullBooleanField(null=True)
    
    # error message from a PayPal transaction
    error = models.CharField(max_length=256, null=True)
    
    # IPN.reason_code
    reason = models.CharField(max_length=64, null=True)
    
    # creation and last modified timestamps
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    # date_payment: when an attempt is made to make the primary payment
    date_payment = models.DateTimeField(null=True)
    
    # date_executed: when an attempt is made to send money to non-primary chained receivers
    date_executed = models.DateTimeField(null=True)
    
    # datetime for creation of preapproval and for its expiration
    date_authorized = models.DateTimeField(null=True)
    date_expired = models.DateTimeField(null=True)
    
    # associated User, Campaign, and Premium for this Transaction
    user = models.ForeignKey(User, null=True)
    campaign = models.ForeignKey(Campaign, null=True)
    premium = models.ForeignKey(Premium, null=True)
    
    # list:  makes allowance for pledging against a Wishlist:  not currently in use
    list = models.ForeignKey(Wishlist, null=True)
    
    # whether the user wants to be not listed publicly
    anonymous = models.BooleanField(null=False)
    
    def save(self, *args, **kwargs):
        if not self.secret:
            self.secret = str(uuid.uuid1())
        super(Transaction, self).save(*args, **kwargs) # Call the "real" save() method.
    
    def __unicode__(self):
        return u"-- Transaction:\n \tstatus: %s\n \t amount: %s\n \treference: %s\n \terror: %s\n" % (self.status, str(self.amount), self.preapproval_key, self.error)
    
    def create_receivers(self, receiver_list):
        
        primary = True
        for r in receiver_list:
            receiver = Receiver.objects.create(email=r['email'], amount=r['amount'], currency=self.currency, status="None", primary=primary, transaction=self)
            primary = False
            
    def get_payment_class(self):
        '''
            Returns the specific payment module that implements this transaction
        '''
        if self.host == PAYMENT_HOST_NONE:
            return None
        else:
            mod = __import__("regluit.payment." + self.host, fromlist=[str(self.host)])
            return mod
                
    
class PaymentResponse(models.Model):
    # The API used
    api = models.CharField(max_length=64, null=False)
    
    # The correlation ID
    correlation_id = models.CharField(max_length=512, null=True)
    
    # the paypal timestamp
    timestamp = models.CharField(max_length=128, null=True)
    
    # extra info we want to store if an error occurs such as the response message
    info = models.CharField(max_length=1024, null=True)
    
    # local status specific to the api call
    status = models.CharField(max_length=32, null=True)
    
    transaction = models.ForeignKey(Transaction, null=False)

    def __unicode__(self):
        return u"PaymentResponse -- api: {0} correlation_id: {1} transaction: {2}".format(self.api, self.correlation_id, unicode(self.transaction))
        
    
class Receiver(models.Model):
    
    email = models.CharField(max_length=64)
    
    amount = models.DecimalField(default=Decimal('0.00'), max_digits=14, decimal_places=2) # max 999,999,999,999.99
    currency = models.CharField(max_length=10)

    status = models.CharField(max_length=64)
    local_status = models.CharField(max_length=64, null=True)
    reason = models.CharField(max_length=64)
    primary = models.BooleanField()
    txn_id = models.CharField(max_length=64)
    transaction = models.ForeignKey(Transaction)
    
    def __unicode__(self):
        return u"Receiver -- email: {0} status: {1} transaction: {2}".format(self.email, self.status, unicode(self.transaction))
    
from django.db.models.signals import post_save, post_delete
import regluit.payment.manager

# handle any save, updates to a payment.Transaction

def handle_transaction_change(sender, instance, created, **kwargs):
    campaign = instance.campaign
    
    if campaign:
        p = regluit.payment.manager.PaymentManager()
        amount = p.query_campaign(campaign=instance.campaign,summary=True)
        instance.campaign.left=instance.campaign.target - amount
        instance.campaign.save()
        
    return True

# handle any deletes of payment.Transaction

def handle_transaction_delete(sender, instance, **kwargs):
    campaign = instance.campaign
    
    if campaign:
        p = regluit.payment.manager.PaymentManager()
        amount = p.query_campaign(campaign=instance.campaign,summary=True)
        instance.campaign.left=instance.campaign.target - amount
        instance.campaign.save()
        
    return True

post_save.connect(handle_transaction_change,sender=Transaction)
post_delete.connect(handle_transaction_delete,sender=Transaction)

