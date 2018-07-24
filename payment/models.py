"""
external library imports
"""
import datetime
import uuid
import logging

from decimal import Decimal

from jsonfield import JSONField

## django imports

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.contrib.sites.models import Site
from django.db.models.signals import post_save, post_delete
from django.utils.http import urlquote
from django.utils.timezone import now

## django module imports

from notification import models as notification


## regluit imports

from regluit.payment.parameters import (
    PAYMENT_TYPE_NONE,
    PAYMENT_TYPE_AUTHORIZATION,

    PAYMENT_HOST_NONE,

    PAYMENT_HOST_CREDIT,

    EXECUTE_TYPE_NONE,
    TRANSACTION_STATUS_NONE,
    TRANSACTION_STATUS_ACTIVE,
    TRANSACTION_STATUS_ERROR,
    TRANSACTION_STATUS_FAILED,
)

from regluit.payment.signals import credit_balance_added, pledge_created
from regluit.utils.localdatetime import date_today

logger = logging.getLogger(__name__)

# in fitting stripe -- here are possible fields to fit in with Transaction
# c.id, c.amount, c.amount_refunded, c.currency, c.description,
# datetime.fromtimestamp(c.created, tz=utc), c.paid,
# c.fee, c.disputed, c.amount_refunded, c.failure_message,
# c.card.fingerprint, c.card.type, c.card.last4, c.card.exp_month, c.card.exp_year

# promising fields

class Transaction(models.Model):

    # type e.g., PAYMENT_TYPE_INSTANT or PAYMENT_TYPE_AUTHORIZATION -- defined in parameters.py
    type = models.IntegerField(default=PAYMENT_TYPE_NONE, null=False)

    # host: the payment processor.
    #Named after the payment module that hosts the payment processing functions
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

    # (RY is not sure what receipt is for; t4u has hijacked this to be an email address for
    # user.is_anonymous to send a receipt to)
    receipt = models.CharField(max_length=256, null=True)

    # whether a Preapproval has been approved or not
    approved = models.NullBooleanField(null=True)

    # error message from a transaction
    error = models.CharField(max_length=256, null=True)

    # IPN.reason_code
    reason = models.CharField(max_length=64, null=True)

    # creation and last modified timestamps
    date_created = models.DateTimeField(auto_now_add=True, db_index=True,)
    date_modified = models.DateTimeField(auto_now=True)

    # date_payment: when an attempt is made to make the primary payment
    date_payment = models.DateTimeField(null=True)

    # date_executed: when an attempt is made to send money to non-primary chained receivers
    date_executed = models.DateTimeField(null=True)

    # datetime for creation of preapproval and for its expiration
    date_authorized = models.DateTimeField(null=True)
    date_expired = models.DateTimeField(null=True)

    # associated User, Campaign, and Premium for this Transaction
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    campaign = models.ForeignKey('core.Campaign', on_delete=models.CASCADE, null=True)
    premium = models.ForeignKey('core.Premium', on_delete=models.CASCADE, null=True)
    offer = models.ForeignKey('core.Offer', on_delete=models.CASCADE, null=True)
    extra = JSONField(null=True, default={})

    # whether the user wants to be not listed publicly
    anonymous = models.BooleanField(default=False)

    # whether the transaction represents a donation
    donation = models.BooleanField(default=False)

    @property
    def tier(self):
        if self.amount < 25:
            return 0
        if self.amount < 50:
            return 1
        if self.amount < 100:
            return 2
        return 3

    @property
    def deadline_or_now(self):
        if self.campaign and self.campaign.deadline:
            return self.campaign.deadline
        return now()

    @property
    def needed_amount(self):
        if self.user is None or self.user.is_anonymous:
            return self.max_amount
        if self.user.credit.available >= self.max_amount:
            return 0
        return self.max_amount - self.user.credit.available

    @property
    def credit_amount(self):
        if self.user is None or self.user.is_anonymous:
            return 0
        if self.user.credit.available >= self.max_amount:
            return self.max_amount
        return self.user.credit.available

    @property
    def ack_link(self):
        return 'https://unglue.it/supporter/%s' % urlquote(self.user.username) if not self.anonymous else ''

    def save(self, *args, **kwargs):
        if not self.secret:
            self.secret = str(uuid.uuid1())
        super(Transaction, self).save(*args, **kwargs) # Call the "real" save() method.

    def __unicode__(self):
        return u"-- Transaction:\n \tstatus: %s\n \t amount: %s\n \terror: %s\n" % (self.status, str(self.amount), self.error)

    def create_receivers(self, receiver_list):

        primary = True
        for r in receiver_list:
            receiver = Receiver.objects.create(
                email=r['email'],
                amount=r['amount'],
                currency=self.currency,
                status="None",
                primary=primary,
                transaction=self
            )
            primary = False

    def get_payment_class(self):
        '''
            Returns the specific payment processor that implements this transaction
        '''
        if self.host == PAYMENT_HOST_NONE:
            return None
        mod = __import__("regluit.payment." + self.host, fromlist=[str(self.host)])
        return mod.Processor()

    def set_executed(self):
        self.date_executed = now()
        self.save()

    def set_payment(self):
        self.date_payment = now()
        self.save()

    def set_credit_approved(self, amount):
        self.amount = amount
        self.host = PAYMENT_HOST_CREDIT
        self.type = PAYMENT_TYPE_AUTHORIZATION
        self.status = TRANSACTION_STATUS_ACTIVE
        self.approved = True
        now_val = now()
        self.date_authorized = now_val
        self.date_expired = now_val + datetime.timedelta(days=settings.PREAPPROVAL_PERIOD)
        self.save()
        pledge_created.send(sender=self, transaction=self)

    def set_pledge_extra(self, pledge_extra):
        if pledge_extra:
            self.anonymous = pledge_extra.anonymous
            self.premium = pledge_extra.premium
            self.offer = pledge_extra.offer
            self.extra.update(pledge_extra.extra)

    def get_pledge_extra(self):
        class pe:
            anonymous = self.anonymous
            premium = self.premium
            offer = self.offer
            extra = self.extra
        return pe

    @classmethod
    def create(cls, amount=0.00, host=PAYMENT_HOST_NONE, max_amount=0.00, currency='USD',
               status=TRANSACTION_STATUS_NONE, campaign=None, user=None, pledge_extra=None,
               donation=False):
        if user and user.is_anonymous:
            user = None
        t = cls.objects.create(
            amount=amount,
            host=host,
            max_amount=max_amount,
            currency=currency,
            status=status,
            campaign=campaign,
            user=user,
            donation=donation,
        )
        if pledge_extra:
            t.set_pledge_extra(pledge_extra)
        return t

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

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=False)

    def __unicode__(self):
        return u"PaymentResponse -- api: {0} correlation_id: {1} transaction: {2}".format(
            self.api,
            self.correlation_id,
            unicode(self.transaction)
        )


class Receiver(models.Model):

    email = models.CharField(max_length=64)

    amount = models.DecimalField(default=Decimal('0.00'), max_digits=14, decimal_places=2) # max 999,999,999,999.99
    currency = models.CharField(max_length=10)

    status = models.CharField(max_length=64)
    local_status = models.CharField(max_length=64, null=True)
    reason = models.CharField(max_length=64)
    primary = models.BooleanField(default=True)
    txn_id = models.CharField(max_length=64)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE,)

    def __unicode__(self):
        return u"Receiver -- email: {0} status: {1} transaction: {2}".format(
            self.email,
            self.status,
            unicode(self.transaction)
        )

class CreditLog(models.Model):
    # a write only record of Unglue.it Credit Transactions
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(default=Decimal('0.00'), max_digits=14, decimal_places=2) # max 999,999,999,999.99
    timestamp = models.DateTimeField(auto_now=True)
    action = models.CharField(max_length=16)
    # used to record the sent id when action = 'deposit'
    sent = models.IntegerField(null=True)

class Credit(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='credit')
    balance = models.DecimalField(default=Decimal('0.00'), max_digits=14, decimal_places=2) # max 999,999,999,999.99
    pledged = models.DecimalField(default=Decimal('0.00'), max_digits=14, decimal_places=2) # max 999,999,999,999.99
    last_activity = models.DateTimeField(auto_now=True)

    @property
    def available(self):
        return self.balance - self.pledged

    def add_to_balance(self, num_credits, notify=True):
        if self.pledged - self.balance > num_credits:  # negative to withdraw
            return False
        else:
            self.balance = self.balance + num_credits
            self.save()
            try: # bad things can happen here if you don't return True
                CreditLog(user=self.user, amount=num_credits, action="add_to_balance").save()
            except:
                logger.exception("failed to log add_to_balance of %s", num_credits)
            if notify:
                try:
                    credit_balance_added.send(sender=self, amount=num_credits)
                except:
                    logger.exception("credit_balance_added notification failed  of %s", num_credits)
            return True

    def add_to_pledged(self, num_credits):
        num_credits = Decimal(num_credits)
        if num_credits is Decimal('NaN'):
            return False
        if self.balance - self.pledged < num_credits:
            return False
        self.pledged = self.pledged + num_credits
        self.save()
        try: # bad things can happen here if you don't return True
            CreditLog(user=self.user, amount=num_credits, action="add_to_pledged").save()
        except:
            logger.exception("failed to log add_to_pledged of %s", num_credits)
        return True

    def use_pledge(self, num_credits):
        num_credits = Decimal(num_credits)
        if num_credits is Decimal('NaN'):
            return False
        if self.pledged < num_credits:
            return False
        self.pledged = self.pledged - num_credits
        self.balance = self.balance - num_credits
        self.save()
        try:
            CreditLog(user=self.user, amount=-num_credits, action="use_pledge").save()
        except:
            logger.exception("failed to log use_pledge of %s", num_credits)
        return True

    def transfer_to(self, receiver, num_credits, notify=True):
        num_credits = Decimal(num_credits)
        if num_credits is Decimal('NaN') or not isinstance(receiver, User):
            logger.info('fail: %s, %s' % (num_credits, receiver))
            return False
        if self.add_to_balance(-num_credits):
            if receiver.credit.add_to_balance(num_credits, notify):
                return True
            # unwind transfer
            self.add_to_balance(num_credits, notify)
            return False
        return False

class Sent(models.Model):
    '''used by gift view to record gifts it has sent'''
    user = models.CharField(max_length=32, null=True)
    amount = models.DecimalField(default=Decimal('0.00'), max_digits=14, decimal_places=2) # max 999,999,999,999.99
    timestamp = models.DateTimeField(auto_now=True)

class Account(models.Model):
    """holds references to accounts at third party payment gateways, especially for representing credit cards"""

    # the following fields from stripe Customer might be relevant to Account
    # -- we need to pick good selection
    # c.id, c.description, c.email, datetime.fromtimestamp(c.created, tz=utc),
    # c.account_balance, c.delinquent,
    # c.active_card.fingerprint, c.active_card.type, c.active_card.last4,
    # c.active_card.exp_month, c.active_card.exp_year,
    # c.active_card.country

    # ACTIVE, DEACTIVATED, EXPIRED, EXPIRING, or ERROR
    STATUS_CHOICES = (
        ('ACTIVE', 'ACTIVE'),
        ('DEACTIVATED', 'DEACTIVATED'),
        ('EXPIRED', 'EXPIRED'),
        ('EXPIRING', 'EXPIRING'),
        ('ERROR', 'ERROR')
    )

    # host: the payment processor.  Named after the payment module that
    # hosts the payment processing functions
    host = models.CharField(default=PAYMENT_HOST_NONE, max_length=32, null=False)
    account_id = models.CharField(max_length=128, null=True)

    # card related info
    card_last4 = models.CharField(max_length=4, null=True)

    # Visa, American Express, MasterCard, Discover, JCB, Diners Club, or Unknown
    card_type = models.CharField(max_length=32, null=True)
    card_exp_month = models.IntegerField(null=True)
    card_exp_year = models.IntegerField(null=True)
    card_fingerprint = models.CharField(max_length=32, null=True)
    card_country = models.CharField(max_length=2, null=True)

    # creation and last modified timestamps
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    date_deactivated = models.DateTimeField(null=True)

    # associated User if any
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    # status variable
    status = models.CharField(max_length=11, choices=STATUS_CHOICES, null=False, default='ACTIVE')

    def deactivate(self):
        """Don't allow more than one active Account of given host to
        be associated with a given user"""
        self.date_deactivated = now()
        self.status = 'DEACTIVATED'
        self.save()

    def calculated_status(self):
        """returns ACTIVE, DEACTIVATED, EXPIRED, EXPIRING, or ERROR"""

    # is it deactivated?

        today = date_today()

        if self.date_deactivated is not None:
            return 'DEACTIVATED'

    # is it expired?

        elif self.card_exp_year < today.year or (
                self.card_exp_year == today.year and self.card_exp_month < today.month
        ):
            return 'EXPIRED'

    # about to expire?  do I want to distinguish from 'ACTIVE'?

        elif self.card_exp_year == today.year and self.card_exp_month == today.month:
            return 'EXPIRING'

    # any transactions w/ errors after the account date?
    # Transaction.objects.filter(host='stripelib', status='Error', approved=True).count()

        elif Transaction.objects.filter(host='stripelib',
                                        status='Error', approved=True, user=self.user
                                       ).filter(date_payment__gt=self.date_created):
            return 'ERROR'
        return 'ACTIVE'


    def update_status(self, value=None, send_notice_on_change_only=True):
        """set Account.status = value unless value is None, in which case,
        we set Account.status=self.calculated_status()
        fire off associated notifications

        By default, send notices only if the status is *changing*.
        Set send_notice_on_change_only = False to
        send notice based on new_status regardless of old status.
        (Useful for initialization)
        """
        old_status = self.status

        if value is None:
            new_status = self.calculated_status()
        else:
            new_status = value

        if new_status == 'EXPIRED':
            self.deactivate()
        elif old_status != new_status:
            self.status = new_status
            self.save()

        # don't notify null users (non-users can buy-to-unglue or thank-for-ungluing)
        if self.user and (not send_notice_on_change_only or (old_status != new_status)):

            logger.info("Account status change: %d %s %s", self.pk, old_status, new_status)

            if new_status == 'EXPIRING':

                logger.info("EXPIRING.  send to instance.user: %s  site: %s", self.user,
                            Site.objects.get_current())

                # fire off an account_expiring notice -- might not want to do this immediately

                notification.queue([self.user], "account_expiring", {
                    'user': self.user,
                    'site':Site.objects.get_current()
                }, True)

            elif new_status == 'EXPIRED':
                logger.info("EXPIRING.  send to instance.user: %s  site: %s", self.user,
                            Site.objects.get_current())

                notification.queue([self.user], "account_expired", {
                    'user': self.user,
                    'site':Site.objects.get_current()
                }, True)

            elif new_status == 'ERROR':
                # TO DO:  what to do?
                pass

            elif new_status == 'DEACTIVATED':
                # nothing needs to happen here
                pass

    def recharge_failed_transactions(self):
        """When a new Account is saved, check whether this is the new active account for a user.
        If so, recharge any outstanding failed transactions
        """
        transactions_to_recharge = self.user.transaction_set.filter(
            (Q(status=TRANSACTION_STATUS_FAILED) | Q(status=TRANSACTION_STATUS_ERROR)) &
            Q(campaign__status='SUCCESSFUL')
        ).all()

        if transactions_to_recharge:
            from regluit.payment.manager import PaymentManager
            pm = PaymentManager()
            for transaction in transactions_to_recharge:
                # check whether we are still within the window to recharge
                if (now() - transaction.deadline_or_now) < datetime.timedelta(settings.RECHARGE_WINDOW):
                    logger.info("Recharging transaction {0} w/ status {1}".format(
                        transaction.id,
                        transaction.status
                    ))
                    pm.execute_transaction(transaction, [])


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

post_save.connect(handle_transaction_change, sender=Transaction)
post_delete.connect(handle_transaction_delete, sender=Transaction)

# handle recharging failed transactions
