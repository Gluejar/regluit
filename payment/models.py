from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from regluit.core.models import Campaign, Wishlist, Premium
from regluit.payment.parameters import *
from regluit.payment.signals import credit_balance_added
from decimal import Decimal, NaN
import uuid
import urllib
import logging
logger = logging.getLogger(__name__)

    
class Transaction(models.Model):
    
    # type e.g., PAYMENT_TYPE_INSTANT or PAYMENT_TYPE_AUTHORIZATION -- defined in parameters.py
    type = models.IntegerField(default=PAYMENT_TYPE_NONE, null=False)
    
    # host: the payment processor.  Named after the payment module that hosts the payment processing functions
    host = models.CharField(default=PAYMENT_HOST_NONE, max_length=32, null=False)
        
    #execution: e.g. EXECUTE_TYPE_CHAINED_INSTANT, EXECUTE_TYPE_CHAINED_DELAYED, EXECUTE_TYPE_PARALLEL
    execution = models.IntegerField(default=EXECUTE_TYPE_NONE, null=False)
    
    # status: general status constants defined in parameters.py
    status = models.CharField(max_length=32, default=TRANSACTION_STATUS_NONE, null=False)
    
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
    
    # how to acknowledge the user on the supporter page of the campaign ebook
    ack_name = models.CharField(max_length=64, null=True)
    ack_dedication = models.CharField(max_length=140, null=True)
    
    # whether the user wants to be not listed publicly
    anonymous = models.BooleanField(null=False)
    
    @property
    def ack_link(self):
        return 'https://unglue.it/supporter/%s'%urllib.urlencode(self.user.username) if not self.anonymous else ''
        
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

class CreditLog(models.Model):
    # a write only record of Donation Credit Transactions
    user = models.ForeignKey(User, null=True) 
    amount = models.DecimalField(default=Decimal('0.00'), max_digits=14, decimal_places=2) # max 999,999,999,999.99
    timestamp = models.DateTimeField(auto_now=True)
    action = models.CharField(max_length=16)
    
class Credit(models.Model):
    user = models.OneToOneField(User, related_name='credit')
    balance = models.DecimalField(default=Decimal('0.00'), max_digits=14, decimal_places=2) # max 999,999,999,999.99
    pledged = models.DecimalField(default=Decimal('0.00'), max_digits=14, decimal_places=2) # max 999,999,999,999.99
    last_activity = models.DateTimeField(auto_now=True)
    
    @property
    def available(self):
        return self.balance - self.pledged
    
    def add_to_balance(self, num_credits):
        if self.pledged - self.balance >  num_credits :  # negative to withdraw
            return False
        else:
            self.balance = self.balance + num_credits
            self.save()
            try: # bad things can happen here if you don't return True
                CreditLog(user = self.user, amount = num_credits, action="add_to_balance").save()
            except:
                logger.exception("failed to log add_to_balance of %s", num_credits)
            try: 
                credit_balance_added.send(sender=self, amount=num_credits)
            except:
                logger.exception("credit_balance_added failed  of %s", num_credits)
            return True
    
    def add_to_pledged(self, num_credits):
        num_credits=Decimal(num_credits)
        if num_credits is NaN:
            return False
        if self.balance - self.pledged <  num_credits :
            return False
        else:
            self.pledged=self.pledged + num_credits
            self.save()
            try: # bad things can happen here if you don't return True
                CreditLog(user = self.user, amount = num_credits, action="add_to_pledged").save()
            except:
                logger.exception("failed to log add_to_pledged of %s", num_credits)
            return True
 
    def use_pledge(self, num_credits):
        if not isinstance( num_credits, int):
            return False
        if self.pledged <  num_credits :
            return False
        else:
            self.pledged=self.pledged - num_credits
            self.balance = self.balance - num_credits
            self.save()
            try:
                CreditLog(user = self.user, amount = - num_credits, action="use_pledge").save()
            except:
                logger.exception("failed to log use_pledge of %s", num_credits)
            return True
            
    def transfer_to(self, receiver, num_credits):
        if not isinstance( num_credits, int) or not isinstance( receiver, User):
            return False
        if self.add_to_balance(-num_credits):
            if receiver.credit.add_to_balance(num_credits):
                return True
            else:
                # unwind transfer
                self.add_to_balance(num_credits)
                return False
        else:
            return False
            
from django.db.models.signals import post_save, post_delete
import regluit.payment.manager

# handle any save, updates to a payment.Transaction

def handle_transaction_change(sender, instance, created, **kwargs):
    campaign = instance.campaign
    if campaign:
        campaign.update_left()
    return True

# handle any deletes of payment.Transaction

def handle_transaction_delete(sender, instance, **kwargs):
    campaign = instance.campaign
    if campaign:
        campaign.update_left()
    return True

post_save.connect(handle_transaction_change,sender=Transaction)
post_delete.connect(handle_transaction_delete,sender=Transaction)

