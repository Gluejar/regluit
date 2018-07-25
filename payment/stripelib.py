# https://github.com/stripe/stripe-python
# https://stripe.com/docs/api?lang=python#top

"""
external library imports
"""
import logging
import json

from datetime import datetime, timedelta
from itertools import islice
from pytz import utc
import re
import unittest
from unittest import TestCase  
  
import stripe

"""
django imports
"""
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.utils.timezone import now

"""
regluit imports
"""
from regluit.payment import baseprocessor
from regluit.payment.models import Account, Transaction, PaymentResponse
from regluit.payment.parameters import (
    PAYMENT_HOST_STRIPE,
    TRANSACTION_STATUS_ACTIVE,
    TRANSACTION_STATUS_COMPLETE,
    TRANSACTION_STATUS_ERROR,
    PAYMENT_TYPE_AUTHORIZATION,
    PAYMENT_TYPE_INSTANT,
    TRANSACTION_STATUS_CANCELED
)
from regluit.payment.signals import transaction_charged, transaction_failed

# as of 2013.07.15
# ['charge.disputed', 'coupon.updated'] are legacy events -- don't know whether to
# include them in list

STRIPE_EVENT_TYPES = ['account.updated', 'account.application.deauthorized', 'balance.available',
    'charge.succeeded', 'charge.failed', 'charge.refunded', 'charge.captured',
    'charge.dispute.created', 'charge.dispute.updated', 'charge.dispute.closed',
    'customer.created', 'customer.updated', 'customer.deleted',
    'customer.card.created', 'customer.card.updated', 'customer.card.deleted',
    'customer.source.created', 'customer.source.deleted', 'customer.source.expiring', 
    'customer.source.updated',
    'customer.subscription.created', 'customer.subscription.updated',
    'customer.subscription.deleted', 'customer.subscription.trial_will_end',
    'customer.discount.created', 'customer.discount.updated',
    'customer.discount.deleted', 'invoice.created', 'invoice.updated',
    'invoice.payment_succeeded', 'invoice.payment_failed', 'invoiceitem.created',
    'invoiceitem.updated', 'invoiceitem.deleted', 'plan.created', 'plan.updated',
    'plan.deleted', 'coupon.created', 'coupon.deleted', 'transfer.created',
    'transfer.updated', 'transfer.paid', 'transfer.failed', 'ping']

logger = logging.getLogger(__name__)

# https://stackoverflow.com/questions/2348317/how-to-write-a-pager-for-python-iterators/2350904#2350904        
def grouper(iterable, page_size):
    page= []
    for item in iterable:
        page.append( item )
        if len(page) == page_size:
            yield page
            page= []
    if len(page):
        yield page

class StripelibError(baseprocessor.ProcessorError):
    pass


# if customer.id doesn't exist, create one and then charge the customer
# we probably should ask our users whether they are ok with our creating a customer id account -- or ask for credit
# card info each time....

# should load the keys for Stripe from db -- but for now just hardcode here
# moving towards not having the stripe api key for the non profit partner in the unglue.it code -- but in a logically
# distinct application

TEST_STRIPE_PK = 'pk_0EajXPn195ZdF7Gt7pCxsqRhNN5BF'
TEST_STRIPE_SK = 'sk_0EajIO4Dnh646KPIgLWGcO10f9qnH'

try:
    from regluit.core.models import Key
    STRIPE_PK = Key.objects.get(name="STRIPE_PK").value
    STRIPE_SK = Key.objects.get(name="STRIPE_SK").value
    logger.info('Successful loading of STRIPE_*_KEYs')
except Exception, e:
    # currently test keys for Gluejar and for raymond.yee@gmail.com as standin for non-profit
    logger.info('Exception {0} Need to use TEST STRIPE_*_KEYs'.format(e))
    STRIPE_PK = TEST_STRIPE_PK
    STRIPE_SK = TEST_STRIPE_SK
    
# set default stripe api_key to that of unglue.it

stripe.api_key =  STRIPE_SK

# maybe we should be able to set this in django.settings...

# to start with, let's try hard-coding the api_version
# https://stripe.com/docs/upgrades?since=2012-07-09#api-changelog

#API_VERSION = '2012-07-09'
API_VERSION = '2013-02-13'
stripe.api_version = API_VERSION

# https://stripe.com/docs/testing

TEST_CARDS = (
    ('4242424242424242', 'Visa'), 
    ('4012888888881881', 'Visa'), 
    ('5555555555554444', 'MasterCard'),
    ('5105105105105100', 'MasterCard'),
    ('378282246310005', 'American Express'),
    ('371449635398431', 'American Express'),
    ('6011111111111117', 'Discover'),
    ('6011000990139424', 'Discover'),
    ('30569309025904', "Diner's Club"),
    ('38520000023237', "Diner's Club"),
    ('3530111333300000', 'JCB'),
    ('3566002020360505','JCB')
)

ERROR_TESTING = dict((
    ('ADDRESS1_ZIP_FAIL', ('4000000000000010', 'address_line1_check and address_zip_check will both fail')),
    ('ADDRESS1_FAIL', ('4000000000000028', 'address_line1_check will fail.')),
    ('ADDRESS_ZIP_FAIL', ('4000000000000036', 'address_zip_check will fail.')),
    ('CVC_CHECK_FAIL', ('4000000000000101', 'cvc_check will fail.')),
    ('BAD_ATTACHED_CARD', ('4000000000000341', 'Attaching this card to a Customer object will succeed, but attempts to charge the customer will fail.')),
    ('CHARGE_DECLINE', ('4000000000000002', 'Charges with this card will always be declined.'))
))

CARD_FIELDS_TO_COMPARE = ('exp_month', 'exp_year', 'name', 'address_line1', 'address_line2', 'address_zip', 'address_state')

# types of errors / when they can be handled

#card_declined: Use this special card number - 4000000000000002.
#incorrect_number: Use a number that fails the Luhn check, e.g. 4242424242424241.
#invalid_expiry_month: Use an invalid month e.g. 13.
#invalid_expiry_year: Use a year in the past e.g. 1970.
#invalid_cvc: Use a two digit number e.g. 99.


def filter_none(d):
    return dict([(k,v) for (k,v) in d.items() if v is not None])
    
# if you create a Customer object, then you'll be able to charge multiple times. You can create a customer with a token.

# https://en.wikipedia.org/wiki/Luhn_algorithm#Implementation_of_standard_Mod_10

def luhn_checksum(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = 0
    checksum += sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d*2))
    return checksum % 10
 
def is_luhn_valid(card_number):
    return luhn_checksum(card_number) == 0
    
    
# https://stripe.com/docs/tutorials/charges

def card (number=TEST_CARDS[0][0], exp_month=1, exp_year=2020, cvc=None, name=None,
          address_line1=None, address_line2=None, address_zip=None, address_state=None, address_country=None):
    
    """Note: there is no place to enter address_city in the API"""
    
    card = {
        "number": number,
        "exp_month": int(exp_month),
        "exp_year": int(exp_year),
        "cvc": int(cvc) if cvc is not None else None,
        "name": name,
        "address_line1": address_line1,
        "address_line2": address_line2,
        "address_zip": address_zip,
        "address_state": address_state,
        "address_country": address_country
    }
    
    return filter_none(card)

def _isListableAPIResource(x):
    """test whether x is an instance of the stripe.ListableAPIResource class"""
    try:
        return issubclass(x, stripe.ListableAPIResource)
    except:
        return False


class StripeClient(object):
    def __init__(self, api_key=STRIPE_SK):
        self.api_key = api_key
    
    # key entities:  Charge, Customer, Token, Event
    
    @property    
    def charge(self):
        return stripe.Charge(api_key=self.api_key)

    @property
    def customer(self):
        return stripe.Customer(api_key=self.api_key)

    @property
    def token(self):
        return stripe.Token(api_key=self.api_key)
        
    @property
    def transfer(self):
        return stripe.Transfer(api_key=self.api_key)
    
    @property    
    def event(self):
        return stripe.Event(api_key=self.api_key)
        
    def create_token(self, card):
        return stripe.Token(api_key=self.api_key).create(card=card)

    def create_customer(self, card=None, description=None, email=None, account_balance=None, plan=None, trial_end=None):
        """card is a dictionary or a token"""
        # https://stripe.com/docs/api?lang=python#create_customer
    
        customer = stripe.Customer(api_key=self.api_key).create(
            card=card,
            description=description,
            email=email,
            account_balance=account_balance,
            plan=plan,
            trial_end=trial_end
        )
        
        # customer.id is useful to save in db
        return customer


    def create_charge(self, amount, currency="usd", customer=None, card=None, description=None ):
    # https://stripe.com/docs/api?lang=python#create_charge
    # customer.id or card required but not both
    # charge the Customer instead of the card
    # amount in cents
    
        charge = stripe.Charge(api_key=self.api_key).create(
            amount=int(100*amount), # in cents
            currency=currency,
            customer=customer,
            card=card,
            description=description
        )
        
        return charge

    def refund_charge(self, charge_id):
        # https://stripe.com/docs/api?lang=python#refund_charge
        ch = stripe.Charge(api_key=self.api_key).retrieve(charge_id)
        ch.refund()
        return ch 
        
    def _all_objs(self, class_type, **kwargs):
        """a generic iterator for all classes of type stripe.ListableAPIResource"""
        # type=None, created=None, count=None, offset=0
        # obj_type: one of  'Charge','Coupon','Customer', 'Event','Invoice', 'InvoiceItem', 'Plan', 'Transfer'

        try:
            stripe_class = getattr(stripe, class_type)
        except:
            yield StopIteration
        else:
            if _isListableAPIResource(stripe_class):
                kwargs2 = kwargs.copy()
                kwargs2.setdefault('offset', 0)
                kwargs2.setdefault('count', 100)  
                        
                more_items = True
                while more_items:
                    
                    items = stripe_class(api_key=self.api_key).all(**kwargs2)['data']
                    for item in items:
                        yield item
                    if len(items):
                        kwargs2['offset'] += len(items)
                    else:
                        more_items = False
            else:
                yield StopIteration
             
    def __getattribute__(self, name):
        """ handle list_* calls"""
        mapping = {'list_charges':"Charge",
                   'list_coupons': "Coupon",
                   'list_customers':"Customer", 
                   'list_events':"Event",
                   'list_invoices':"Invoice",
                   'list_invoiceitems':"InvoiceItem",
                   'list_plans':"Plan",
                   'list_transfers':"Transfer"
                    }
        if name in mapping.keys():
            class_value = mapping[name]
            def list_events(**kwargs):
                for e in self._all_objs(class_value, **kwargs):
                    yield e                
            return list_events                    
        else:
            return object.__getattribute__(self, name)
            
            


            
# can't test Transfer in test mode: "There are no transfers in test mode."

#pledge scenario
# bad card -- what types of erros to handle?
# https://stripe.com/docs/api#errors


# https://stripe.com/docs/api#event_types
# events of interest -- especially ones that do not directly arise immediately (synchronously) from something we do -- I think
# especially:  charge.disputed
# I think following (charge.succeeded, charge.failed, charge.refunded) pretty much sychronous to our actions
# customer.created, customer.updated, customer.deleted

# transfer
# I expect the ones related to transfers all happen asynchronously: transfer.created, transfer.updated, transfer.failed

# When will the money I charge with Stripe end up in my bank account?
# Every day, we transfer the money that you charged seven days previously?that is, you receive the money for your March 1st charges on March 8th.

# pending payments?
# how to tell whether money transferred to bank account yet
# best practices for calling Events -- not too often.


#  Errors we still need to catch:
#
#   * invalid_number -- can't get stripe to generate for us.  What it means: 
#
#      * that the card has been cancelled (or never existed to begin with
#
#      * the card is technically correct (Luhn valid?)
#
#      * the first 6 digits point to a valid bank
#
#      * but the account number (the rest of the digits) doesn't correspond to a credit account with that bank
#
#      * Brian of stripe.com suggests we could treat it the same way as we'd treat card_declined
#
#   * processing_error:
#
#      * means: something went wrong when stripe tried to make the charge (it could be that the card's issuing bank is down, or our connection to the bank isn't working properly)
#      * we can retry -- e.g.,  a minute later, then 30 minutes, then an hour, 3 hours, a day.
#      * we shouldn't see processing_error very often
#
#   * expired_card -- also not easily simulatable in test mode



class StripeErrorTest(TestCase):
    """Make sure the exceptions returned by stripe act as expected"""
    
    def test_cc_test_numbers_luhn_valid(self):
        """Show that the test CC numbers supplied for testing as valid numbers are indeed Luhn valid"""
        self.assertTrue(all([is_luhn_valid(c[0]) for c in ERROR_TESTING.values()]))
        
    def test_good_token(self):
        """ verify normal operation """
        sc = StripeClient()
        card1 = card(number=TEST_CARDS[0][0], exp_month=1, exp_year='2020', cvc='123', name='Don Giovanni',
          address_line1="100 Jackson St.", address_line2="", address_zip="94706", address_state="CA", address_country=None)  # good card
        token1 = sc.create_token(card=card1)
        # use the token id -- which is what we get from JavaScript api -- and retrieve the token
        token2 = sc.token.retrieve(id=token1.id)
        self.assertEqual(token2.id, token1.id)
        # make sure token id has a form tok_
        self.assertEqual(token2.id[:4], "tok_")
        
        # should be only test mode
        self.assertEqual(token2.livemode, False)
        # token hasn't been used yet
        self.assertEqual(token2.used, False)
        # test that card info matches up with what was fed in.
        for k in CARD_FIELDS_TO_COMPARE:
            self.assertEqual(token2.card[k], card1[k])
        # last4
        self.assertEqual(token2.card.last4,  TEST_CARDS[0][0][-4:])
        # fingerprint
        self.assertGreaterEqual(len(token2.card.fingerprint), 16)
        
        # now charge the token
        charge1 = sc.create_charge(10, 'usd', card=token2.id)
        self.assertEqual(charge1.amount, 1000)
        self.assertEqual(charge1.id[:3], "ch_")
        # dispute, failure_message, fee, fee_details
        self.assertEqual(charge1.dispute,None)
        self.assertEqual(charge1.failure_message,None)
        self.assertEqual(charge1.fee,59)
        self.assertEqual(charge1.refunded,False)
        
        
    def test_error_creating_customer_with_declined_card(self):
        """Test whether we can get a charge decline error"""
        sc = StripeClient()
        card1 = card(number=ERROR_TESTING['CHARGE_DECLINE'][0])
        try:
            cust1 = sc.create_customer(card=card1, description="This card should fail")
            self.fail("Attempt to create customer did not throw expected exception.")
        except stripe.CardError as e:
            self.assertEqual(e.code, "card_declined")
            self.assertEqual(e.args[0], "Your card was declined")
            
    def test_charge_bad_cust(self):
        # expect the card to be declined -- and for us to get CardError
        sc = StripeClient()
        # bad card
        card1 = card(number=ERROR_TESTING['BAD_ATTACHED_CARD'][0])
        # attaching card should be ok
        cust1 = sc.create_customer(card=card1, description="test bad customer", email="rdhyee@gluejar.com")
        # trying to charge the card should fail
        self.assertRaises(stripe.CardError, sc.create_charge, 10,
                          customer = cust1.id, description="$10 for bad cust")

    def test_bad_cc_number(self):
        """send a bad cc and should get an error when trying to create a token"""
        BAD_CC_NUM = '4242424242424241'
        
        # reason for decline is number is not Luhn valid
        self.assertFalse(is_luhn_valid(BAD_CC_NUM))
        
        sc = StripeClient()
        card1 = card(number=BAD_CC_NUM, exp_month=1, exp_year=2020, cvc='123', name='Don Giovanni',
          address_line1="100 Jackson St.", address_line2="", address_zip="94706", address_state="CA", address_country=None)  # good card
            
        try:
            token1 = sc.create_token(card=card1)
            self.fail("Attempt to create token with bad cc number did not throw expected exception.")
        except stripe.CardError as e:
            self.assertEqual(e.code, "incorrect_number")
            self.assertEqual(e.args[0], "Your card number is incorrect")
            
    def test_invalid_expiry_month(self):
        """Use an invalid month e.g. 13."""
        
        sc = StripeClient()
        card1 = card(number=TEST_CARDS[0][0], exp_month=13, exp_year=2020, cvc='123', name='Don Giovanni',
          address_line1="100 Jackson St.", address_line2="", address_zip="94706", address_state="CA", address_country=None)

        try:
            token1 = sc.create_token(card=card1)
            self.fail("Attempt to create token with invalid expiry month did not throw expected exception.")
        except stripe.CardError as e:
            self.assertEqual(e.code, "invalid_expiry_month")
            self.assertEqual(e.args[0], "Your card's expiration month is invalid")

    def test_invalid_expiry_year(self):
        """Use a year in the past e.g. 1970."""
        
        sc = StripeClient()
        card1 = card(number=TEST_CARDS[0][0], exp_month=12, exp_year=1970, cvc='123', name='Don Giovanni',
          address_line1="100 Jackson St.", address_line2="", address_zip="94706", address_state="CA", address_country=None)

        try:
            token1 = sc.create_token(card=card1)
            self.fail("Attempt to create token with invalid expiry year did not throw expected exception.")
        except stripe.CardError as e:
            self.assertEqual(e.code, "invalid_expiry_year")
            self.assertEqual(e.args[0], "Your card's expiration year is invalid")
            
    def test_invalid_cvc(self):
        """Use a two digit number e.g. 99."""
        
        sc = StripeClient()
        card1 = card(number=TEST_CARDS[0][0], exp_month=12, exp_year=2020, cvc='99', name='Don Giovanni',
          address_line1="100 Jackson St.", address_line2="", address_zip="94706", address_state="CA", address_country=None)

        try:
            token1 = sc.create_token(card=card1)
            self.fail("Attempt to create token with invalid cvc did not throw expected exception.")
        except stripe.CardError as e:
            self.assertEqual(e.code, "invalid_cvc")
            self.assertEqual(e.args[0], "Your card's security code is invalid")
            
    def test_missing_card(self):
        """There is no card on a customer that is being charged"""
        
        sc = StripeClient()
        # create a Customer with no attached card
        cust1 = sc.create_customer(description="test cust w/ no card")
        try:
            sc.create_charge(10, customer = cust1.id, description="$10 for cust w/ no card")
        except stripe.CardError as e:
            self.assertEqual(e.code, "missing")
            self.assertEqual(e.args[0], "Cannot charge a customer that has no active card")
 
class PledgeScenarioTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls._sc = StripeClient(api_key=STRIPE_SK)
        
        # valid card
        card0 = card()
        cls._good_cust = cls._sc.create_customer(card=card0, description="test good customer", email="raymond.yee@gmail.com")
        
        # bad card
        test_card_num_to_get_BAD_ATTACHED_CARD = ERROR_TESTING['BAD_ATTACHED_CARD'][0]
        card1 = card(number=test_card_num_to_get_BAD_ATTACHED_CARD)
        cls._cust_bad_card = cls._sc.create_customer(card=card1, description="test bad customer", email="rdhyee@gluejar.com")
    
    def test_charge_good_cust(self):
        charge = self._sc.create_charge(10, customer=self._good_cust.id, description="$10 for good cust")
        self.assertEqual(type(charge.id), unicode)

        # print out all the pieces of Customer and Charge objects
        print dir(charge)
        print dir(self._good_cust)
        
    def test_error_creating_customer_with_declined_card(self):
        # should get a CardError upon attempt to create Customer with this card
        _card = card(number=card(ERROR_TESTING['CHARGE_DECLINE'][0]))
        self.assertRaises(stripe.CardError, self._sc.create_customer, card=_card)
    
    def test_charge_bad_cust(self):
        # expect the card to be declined -- and for us to get CardError
        self.assertRaises(stripe.CardError, self._sc.create_charge, 10,
                          customer = self._cust_bad_card.id, description="$10 for bad cust")
        
    @classmethod
    def tearDownClass(cls):
        # clean up stuff we create in test -- right now list current objects

        pass
    
        #cls._good_cust.delete()
        
        #print "list of customers"
        #print [(i, c.id, c.description, c.email, datetime.fromtimestamp(c.created, tz=utc), c.account_balance, c.delinquent, c.active_card.fingerprint, c.active_card.type, c.active_card.last4, c.active_card.exp_month, c.active_card.exp_year, c.active_card.country) for(i,  c) in enumerate(cls._sc.customer.all()["data"])]
        #
        #print "list of charges"
        #print [(i, c.id, c.amount, c.amount_refunded, c.currency, c.description, datetime.fromtimestamp(c.created, tz=utc), c.paid, c.fee, c.disputed, c.amount_refunded, c.failure_message, c.card.fingerprint, c.card.type, c.card.last4, c.card.exp_month, c.card.exp_year) for (i, c) in enumerate(cls._sc.charge.all()['data'])]
        #
        ## can retrieve events since a certain time?
        #print "list of events", cls._sc.event.all()
        #print [(i, e.id, e.type, e.created, e.pending_webhooks, e.data) for (i,e) in enumerate(cls._sc.event.all()['data'])]

class StripePaymentRequest(baseprocessor.BasePaymentRequest):
    """so far there is no need to have a separate class here"""
    pass

class Processor(baseprocessor.Processor):
    
    def make_account(self, user=None, token=None, email=None):
        """returns a payment.models.Account based on stripe token and user"""
        
        if token is None or len(token) == 0:
           raise StripelibError("input token is None", None)

        sc = StripeClient()
        
        # create customer and charge id and then charge the customer
        try:
            if user:
                customer = sc.create_customer(card=token, description=user.username,
                                      email=user.email)
            else:
                customer = sc.create_customer(card=token, description='anonymous user', email=email)
        except stripe.StripeError as e:
            raise StripelibError(e.args, e)
            
        account = Account(host = PAYMENT_HOST_STRIPE,
                          account_id = customer.id,
                          card_last4 = customer.active_card.last4,
                          card_type = customer.active_card.type,
                          card_exp_month = customer.active_card.exp_month,
                          card_exp_year = customer.active_card.exp_year,
                          card_fingerprint = customer.active_card.fingerprint,
                          card_country = customer.active_card.country,
                          user = user
                          )
        if user and user.profile.account:
            user.profile.account.deactivate()
            account.save()  
            account.recharge_failed_transactions() 
        else:
            account.save()
        return account
        
    class Preapproval(StripePaymentRequest, baseprocessor.Processor.Preapproval):
        
        def __init__( self, transaction, amount, expiry=None, return_url=None,  paymentReason=""):
          
            # set the expiration date for the preapproval if not passed in.  This is what the paypal library does
            
            self.transaction = transaction
            
            now_val = now()
            if expiry is None:
                expiry = now_val + timedelta( days=settings.PREAPPROVAL_PERIOD )
            transaction.date_authorized = now_val
            transaction.date_expired = expiry
              
            # let's figure out what part of transaction can be used to store info
            # try placing charge id in transaction.pay_key
            # need to set amount
            # how does transaction.max_amount get set? -- coming from /pledge/xxx/ -> manager.process_transaction
            # max_amount is set -- but I don't think we need it for stripe
    
            # ASSUMPTION:  a user has any given moment one and only one active payment Account
    
            account = transaction.user.profile.account
            if not account:
                logger.warning("user {0} has no active payment account".format(transaction.user))
                raise StripelibError("user {0} has no active payment account".format(transaction.user))
                    
            logger.info("user: {0} customer.id is {1}".format(transaction.user, account.account_id))
            
            # settings to apply to transaction for TRANSACTION_STATUS_ACTIVE
            # should approved be set to False and wait for a webhook?
            transaction.approved = True
            transaction.type = PAYMENT_TYPE_AUTHORIZATION
            transaction.host = PAYMENT_HOST_STRIPE
            transaction.status = TRANSACTION_STATUS_ACTIVE
        
            transaction.preapproval_key = account.account_id
            
            transaction.currency = 'USD'
            transaction.amount = amount
            
            transaction.save()
            
        def key(self):
            return self.transaction.preapproval_key
        
        def next_url(self):
            """return None because no redirection to stripe is required"""
            return None
      
    class Pay(StripePaymentRequest, baseprocessor.Processor.Pay):
    
      '''
        The pay function generates a redirect URL to approve the transaction
        If the transaction has a null user (is_anonymous), then a token musr be supplied
      '''
        
      def __init__( self, transaction, return_url=None,  amount=None, paymentReason="", token=None):
        self.transaction=transaction
        self.url = return_url
          
        now_val = now()                   
        transaction.date_authorized = now_val
          
        # ASSUMPTION:  a user has any given moment one and only one active payment Account
        if token:
            # user is anonymous
            account =  transaction.get_payment_class().make_account(token = token, email = transaction.receipt)
        else:
            account = transaction.user.profile.account        
        
        if not account:
            logger.warning("user {0} has no active payment account".format(transaction.user))
            raise StripelibError("user {0} has no active payment account".format(transaction.user))
                
        logger.info("user: {0} customer.id is {1}".format(transaction.user, account.account_id))
        
        # settings to apply to transaction for TRANSACTION_STATUS_ACTIVE
        # should approved be set to False and wait for a webhook?
        transaction.approved = True
        transaction.type = PAYMENT_TYPE_INSTANT
        transaction.host = PAYMENT_HOST_STRIPE
    
        transaction.preapproval_key = account.account_id
        
        transaction.currency = 'USD'
        transaction.amount = amount
        
        transaction.save()
        
        # execute the transaction
        p = transaction.get_payment_class().Execute(transaction)
        
        if p.success() and not p.error():
            transaction.pay_key = p.key()
            transaction.save()
        else:
            self.errorMessage = p.errorMessage #pass error message up
            logger.info("execute_transaction Error: {}".format(p.error_string()))
                    
      def amount( self ):
          return self.transaction.amount
          
      def key( self ):
          return self.transaction.pay_key
    
      def next_url( self ):
          return self.url
        
    class Execute(StripePaymentRequest):
        
        '''
            The Execute function attempts to charge the credit card of stripe Customer associated with user connected to transaction.
        '''
        
        def __init__(self, transaction=None):
            
            self.transaction = transaction
            
            # make sure transaction hasn't already been executed
            if transaction.status == TRANSACTION_STATUS_COMPLETE:
                return
            # make sure we are dealing with a stripe transaction
            if transaction.host <> PAYMENT_HOST_STRIPE:
                raise StripelibError("transaction.host {0} is not the expected {1}".format(transaction.host, PAYMENT_HOST_STRIPE))
            
            sc = StripeClient()
            
            # look first for transaction.user.profile.account.account_id
            try:
                customer_id = transaction.user.profile.account.account_id
            except:
                customer_id = transaction.preapproval_key
            
            if customer_id is not None:    
                try:
                    # useful things to put in description: transaction.id, transaction.user.id,  customer_id, transaction.amount
                    charge = sc.create_charge(transaction.amount, customer=customer_id,
                                              description=json.dumps({"t.id":transaction.id,
                                                                      "email":transaction.user.email if transaction.user else transaction.receipt,
                                                                      "cus.id":customer_id,
                                                                      "tc.id": transaction.campaign.id if transaction.campaign else '0',
                                                                      "amount": float(transaction.amount)}))
                except stripe.StripeError as e:
                    # what to record in terms of errors?  (error log?)
                    # use PaymentResponse to store error

                    r = PaymentResponse.objects.create(api="stripelib.Execute", correlation_id=None,
                                                       timestamp=now(), info=e.args[0],
                                                       status=TRANSACTION_STATUS_ERROR, transaction=transaction)
                    
                    transaction.status = TRANSACTION_STATUS_ERROR	  	
                    self.errorMessage = e.args # manager puts this on transaction
                    transaction.save()

                    # fire off the fact that transaction failed -- should actually do so only if not a transient error
                    # if card_declined or expired card, ask user to update account
                    if isinstance(e, stripe.CardError) and e.code in ('card_declined', 'expired_card', 'incorrect_number', 'processing_error'):
                        transaction_failed.send(sender=self, transaction=transaction)
                    # otherwise, report exception to us
                    else:
                        logger.exception("transaction id {0}, exception: {1}".format(transaction.id,  e.args))
                    
                    
                else:
                    self.charge = charge
                    
                    transaction.status = TRANSACTION_STATUS_COMPLETE
                    transaction.pay_key = charge.id
                    transaction.date_payment = now()
                    transaction.save()
                    
                    # fire signal for sucessful transaction
                    transaction_charged.send(sender=self, transaction=transaction)

                    
            else:
                # nothing to charge
                raise StripelibError("No customer id available to charge for transaction {0}".format(transaction.id), None)
    
    
        def api(self):
            return "Base Pay"
        
        def key(self):
            # IN paypal land, our key is updated from a preapproval to a pay key here, just return the existing key
            return self.transaction.pay_key
        
    class PreapprovalDetails(StripePaymentRequest):
        '''
           Get details about an authorized token
           
           This api must set 4 different class variables to work with the code in manager.py
           
           status - one of the global transaction status codes
           approved - boolean value
           currency - not used in this API, but we can get some more info via other APIs - TODO
           amount - not used in this API, but we can get some more info via other APIs - TODO
           
        '''
        def __init__(self, transaction):
     
            self.transaction = transaction
            self.status = self.transaction.status
            if self.status == TRANSACTION_STATUS_CANCELED:
                self.approved = False
            else:
                self.approved = True
    
            # Set the other fields that are expected.  We don't have values for these now, so just copy the transaction
            self.currency = transaction.currency
            self.amount = transaction.amount
            
    def ProcessIPN(self, request):
        # retrieve the request's body and parse it as JSON in, e.g. Django
        try:
            event_json = json.loads(request.body)
        except ValueError, e:
            # not able to parse request.body -- throw a "Bad Request" error
            logger.warning("Non-json being sent to Stripe IPN: {0}".format(e))
            return HttpResponse(status=400)
        else:
            # now parse out pieces of the webhook
            event_id = event_json.get("id")
            # use Stripe to ask for details -- ignore what we're sent for security
            
            sc = StripeClient()
            try:
                event = sc.event.retrieve(event_id)
            except stripe.InvalidRequestError:
                logger.warning("Invalid Event ID: {0}".format(event_id))
                return HttpResponse(status=400)
            else:
                event_type = event.get("type")
                if event_type not in STRIPE_EVENT_TYPES:
                    logger.warning("Unrecognized Stripe event type {0} for event {1}".format(event_type, event_id))
                    # is this the right code to respond with?
                    return HttpResponse(status=400)
                # https://stripe.com/docs/api?lang=python#event_types -- type to delegate things
                # parse out type as resource.action

                try:
                    (resource, action) = re.match("^(.+)\.([^\.]*)$", event_type).groups()
                except Exception, e:
                    logger.warning("Parsing of event_type into resource, action failed: {0}".format(e))
                    return HttpResponse(status=400)
                
                try:
                    ev_object = event.data.object
                except Exception, e:
                    logger.warning("attempt to retrieve event object failed: {0}".format(e))                            
                    return HttpResponse(status=400)
                
                if event_type == 'account.updated':
                    # should we alert ourselves?
                    # how about account.application.deauthorized ?
                    pass
                elif resource == 'charge':
                    # we need to handle: succeeded, failed, refunded, disputed
                    
                    if action == 'succeeded':
                        # TO DO:  delete this logic since we don't do anything but look up transaction.
                        logger.info("charge.succeeded webhook for {0}".format(ev_object.get("id")))
                        # try to parse description of object to pull related transaction if any
                        # wrapping this in a try statement because it possible that we have a charge.succeeded outside context of unglue.it
                        try:
                            charge_meta = json.loads(ev_object["description"])
                            transaction = Transaction.objects.get(id=charge_meta["t.id"])
                            # now check that account associated with the transaction matches
                            # ev.data.object.id, t.pay_key
                            if ev_object.id == transaction.pay_key:
                                logger.info("ev_object.id == transaction.pay_key: {0}".format(ev_object.id))
                            else:
                                logger.warning("ev_object.id {0} <> transaction.pay_key {1}".format(ev_object.id, transaction.pay_key))
                        except Exception, e:
                            logger.warning(e)    
                            
                    elif action == 'failed':
                        # TO DO:  delete this logic since we don't do anything but look up transaction.
                        logger.info("charge.failed webhook for {0}".format(ev_object.get("id")))
                        try:
                            charge_meta = json.loads(ev_object["description"])
                            transaction = Transaction.objects.get(id=charge_meta["t.id"])
                            # now check that account associated with the transaction matches
                            # ev.data.object.id, t.pay_key
                            if ev_object.id == transaction.pay_key:
                                logger.info("ev_object.id == transaction.pay_key: {0}".format(ev_object.id))
                            else:
                                logger.warning("ev_object.id {0} <> transaction.pay_key {1}".format(ev_object.id, transaction.pay_key))

                        except Exception, e:
                            logger.warning(e)
                    elif action == 'refunded':
                        pass
                    elif action == 'disputed':
                        pass                    
                    else:
                        # unexpected
                        pass
                elif resource == 'customer':
                    if action == 'created':
                        # test application: email Raymond
                        # do we have a flag to indicate production vs non-production? -- or does it matter?
                        # email RY whenever a new Customer created -- we probably want to replace this with some other
                        # more useful long tem action.
                        send_mail(u"Stripe Customer (id {0};  description: {1}) created".format(ev_object.get("id"),
                                                                        ev_object.get("description")),
                                  u"Stripe Customer email: {0}".format(ev_object.get("email")),
                                  "notices@gluejar.com",
                                  ["rdhyee@gluejar.com"])
                        logger.info("email sent for customer.created for {0}".format(ev_object.get("id")))
                    # handle updated, deleted
                    else:
                        pass
                else:  # other events
                    pass
                
                return HttpResponse("event_id: {0} event_type: {1}".format(event_id, event_type))


def suite():
    
    testcases = [PledgeScenarioTest, StripeErrorTest]
    #testcases = [StripeErrorTest]
    suites = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(testcase) for testcase in testcases])
    #suites.addTest(LibraryThingTest('test_cache'))
    #suites.addTest(SettingsTest('test_dev_me_alignment'))  # give option to test this alignment
    return suites


# IPNs/webhooks: https://stripe.com/docs/webhooks
# how to use pending_webhooks ?

# all events
# https://stripe.com/docs/api?lang=python#list_events

if __name__ == '__main__':
    #unittest.main()
    suites = suite()
    #suites = unittest.defaultTestLoader.loadTestsFromModule(__import__('__main__'))
    unittest.TextTestRunner().run(suites)    
