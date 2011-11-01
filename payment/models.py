from django.db import models
from django.contrib.auth.models import User
from regluit.core.models import Campaign, Wishlist
from regluit.payment.parameters import *
from decimal import Decimal
import uuid

class Transaction(models.Model):
    
    type = models.IntegerField(default=PAYMENT_TYPE_NONE, null=False)
    target = models.IntegerField(default=TARGET_TYPE_NONE, null=False)
    status = models.CharField(max_length=32, default='NONE', null=False)
    amount = models.DecimalField(default=Decimal('0.00'), max_digits=14, decimal_places=2) # max 999,999,999,999.99
    currency = models.CharField(max_length=10, default='USD', null=True)
    secret = models.CharField(max_length=64)
    reference = models.CharField(max_length=128, null=True)
    receipt = models.CharField(max_length=256, null=True)
    error = models.CharField(max_length=256, null=True)
    reason = models.CharField(max_length=64, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    date_payment = models.DateTimeField(null=True)
    date_authorized = models.DateTimeField(null=True)
    date_expired = models.DateTimeField(null=True)
    user = models.ForeignKey(User, null=True)
    campaign = models.ForeignKey(Campaign, null=True)
    list = models.ForeignKey(Wishlist, null=True)
    anonymous = models.BooleanField(null=False)
    
    def save(self, *args, **kwargs):
        if not self.secret:
            self.secret = str(uuid.uuid1())
        super(Transaction, self).save(*args, **kwargs) # Call the "real" save() method.
    
    def __unicode__(self):
        return u"-- Transaction:\n \tstatus: %s\n \t amount: %s\n \treference: %s\n \terror: %s\n" % (self.status, str(self.amount), self.reference, self.error)
    
    def create_receivers(self, receiver_list):
        
        primary = True
        for r in receiver_list:
            receiver = Receiver.objects.create(email=r['email'], amount=r['amount'], currency=self.currency, status="None", primary=primary, transaction=self)
            primary = False
                
    
class Receiver(models.Model):
    
    email = models.CharField(max_length=64)
    amount = models.DecimalField(default=Decimal('0.00'), max_digits=14, decimal_places=2) # max 999,999,999,999.99
    currency = models.CharField(max_length=10)
    status = models.CharField(max_length=64)
    reason = models.CharField(max_length=64)
    primary = models.BooleanField()
    txn_id = models.CharField(max_length=64)
    transaction = models.ForeignKey(Transaction)
    
    