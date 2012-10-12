# https://github.com/stripe/stripe-python
# https://stripe.com/docs/api?lang=python#top

import logging
from datetime import datetime, timedelta
from pytz import utc

from django.conf import settings

from regluit.payment.models import Account
from regluit.payment.parameters import PAYMENT_HOST_STRIPE
from regluit.payment.parameters import TRANSACTION_STATUS_ACTIVE, TRANSACTION_STATUS_COMPLETE, PAYMENT_TYPE_AUTHORIZATION, TRANSACTION_STATUS_CANCELED
from regluit.payment import baseprocessor
from regluit.utils.localdatetime import now, zuluformat

import stripe

logger = logging.getLogger(__name__)

class StripelibError(baseprocessor.ProcessorError):
    pass

try:
    import unittest
    from unittest import TestCase    
except:
    from django.test import TestCase
    from django.utils import unittest

# if customer.id doesn't exist, create one and then charge the customer
# we probably should ask our users whether they are ok with our creating a customer id account -- or ask for credit
# card info each time....

# should load the keys for Stripe from db -- but for now just hardcode here
# moving towards not having the stripe api key for the non profit partner in the unglue.it code -- but in a logically
# distinct application

try:
    from regluit.core.models import Key
    STRIPE_PK = Key.objects.get(name="STRIPE_PK").value
    STRIPE_SK = Key.objects.get(name="STRIPE_SK").value
    logger.info('Successful loading of STRIPE_*_KEYs')
except Exception, e:
    # currently test keys for Gluejar and for raymond.yee@gmail.com as standin for non-profit
    STRIPE_PK = 'pk_0EajXPn195ZdF7Gt7pCxsqRhNN5BF'
    STRIPE_SK = 'sk_0EajIO4Dnh646KPIgLWGcO10f9qnH'
    
# set default stripe api_key to that of unglue.it

stripe.api_key =  STRIPE_SK   

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

# http://en.wikipedia.org/wiki/Luhn_algorithm#Implementation_of_standard_Mod_10

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

    def list_all_charges(self, count=None, offset=None, customer=None):
        # https://stripe.com/docs/api?lang=python#list_charges
        return stripe.Charge(api_key=self.api_key).all(count=count, offset=offset, customer=customer)
   

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
        # disputed, failure_message, fee, fee_details
        self.assertEqual(charge1.disputed,False)
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
            self.assertEqual(e.message, "Your card was declined.")
            
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
            self.assertEqual(e.message, "Your card number is incorrect")
            
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
            self.assertEqual(e.message, "Your card's expiration month is invalid")

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
            self.assertEqual(e.message, "Your card's expiration year is invalid")
            
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
            self.assertEqual(e.message, "Your card's security code is invalid")
            
    def test_missing_card(self):
        """There is no card on a customer that is being charged"""
        
        sc = StripeClient()
        # create a Customer with no attached card
        cust1 = sc.create_customer(description="test cust w/ no card")
        try:
            sc.create_charge(10, customer = cust1.id, description="$10 for cust w/ no card")
        except stripe.CardError as e:
            self.assertEqual(e.code, "missing")
            self.assertEqual(e.message, "Cannot charge a customer that has no active card")

        

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
        self.assertEqual(type(charge.id), str)

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

        #cls._good_cust.delete()
        
        print "list of customers"
        print [(i, c.id, c.description, c.email, datetime.fromtimestamp(c.created, tz=utc), c.account_balance, c.delinquent, c.active_card.fingerprint, c.active_card.type, c.active_card.last4, c.active_card.exp_month, c.active_card.exp_year, c.active_card.country) for(i,  c) in enumerate(cls._sc.customer.all()["data"])]
        
        print "list of charges"
        print [(i, c.id, c.amount, c.amount_refunded, c.currency, c.description, datetime.fromtimestamp(c.created, tz=utc), c.paid, c.fee, c.disputed, c.amount_refunded, c.failure_message, c.card.fingerprint, c.card.type, c.card.last4, c.card.exp_month, c.card.exp_year) for (i, c) in enumerate(cls._sc.charge.all()['data'])]
        
        # can retrieve events since a certain time?
        print "list of events", cls._sc.event.all()
        print [(i, e.id, e.type, e.created, e.pending_webhooks, e.data) for (i,e) in enumerate(cls._sc.event.all()['data'])]

class StripePaymentRequest(baseprocessor.BasePaymentRequest):
    """so far there is no need to have a separate class here"""
    pass

class Processor(baseprocessor.Processor):
    
    def make_account(self, user, token=None):
        """returns a payment.models.Account based on stripe token and user"""
        
        sc = StripeClient()
        
        # allow for the possibility that if token is None, just create a placeholder Account
        
        if token is not None:
        
            # create customer and charge id and then charge the customer
            try:
                customer = sc.create_customer(card=token, description=user.username,
                                          email=user.email)
            except stripe.StripeError as e:
                raise StripelibError(e.message, e)
                
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
        
            account.save()
        
        else:
            account = Account(host = PAYMENT_HOST_STRIPE, user= user)
            account.save()
        
        return account
    
    class Pay(StripePaymentRequest, baseprocessor.Processor.Pay):
        pass
        
    class Preapproval(StripePaymentRequest, baseprocessor.Processor.Preapproval):
        
        def __init__( self, transaction, amount, expiry=None, return_url=None,  paymentReason=""):
          
            # set the expiration date for the preapproval if not passed in.  This is what the paypal library does
            
            self.transaction = transaction
            
            now_val = now()
            if expiry is None:
                expiry = now_val + timedelta( days=settings.PREAPPROVAL_PERIOD )
            transaction.date_authorized = now_val
            transaction.date_expired = expiry
              
            sc = StripeClient()
            
            # let's figure out what part of transaction can be used to store info
            # try placing charge id in transaction.pay_key
            # need to set amount
            # how does transaction.max_amount get set? -- coming from /pledge/xxx/ -> manager.process_transaction
            # max_amount is set -- but I don't think we need it for stripe
    
            # ASSUMPTION:  a user has any given moment one and only one active payment Account
    
            if transaction.user.account_set.filter(date_deactivated__isnull=True).count() > 1:
                logger.warning("user {0} has more than one active payment account".format(transaction.user))
            elif transaction.user.account_set.filter(date_deactivated__isnull=True).count() == 0:
                logger.warning("user {0} has no active payment account".format(transaction.user))
                raise StripelibError("user {0} has no active payment account".format(transaction.user))
                    
            account = transaction.user.account_set.filter(date_deactivated__isnull=True)[0]
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
      
      
    class Execute(StripePaymentRequest):
        
        '''
            The Execute function sends an existing token(generated via the URL from the pay operation), and collects
            the money.
        '''
        
        def __init__(self, transaction=None):
            self.transaction = transaction
            
            # execute transaction
            assert transaction.host == PAYMENT_HOST_STRIPE
            
            sc = StripeClient()
            
            # look at transaction.preapproval_key
            # is it a customer or a token?
            
            # BUGBUG:  replace description with somethin more useful
            # TO DO: rewrapping StripeError to StripelibError -- but maybe we should be more specific
            if transaction.preapproval_key.startswith('cus_'):
                try:
                    charge = sc.create_charge(transaction.amount, customer=transaction.preapproval_key, description="${0} for test / retain cc".format(transaction.amount))
                except stripe.StripeError as e:
                    raise StripelibError(e.message, e)
            elif transaction.preapproval_key.startswith('tok_'):
                try:
                    charge = sc.create_charge(transaction.amount, card=transaction.preapproval_key, description="${0} for test / cc not retained".format(transaction.amount))
                except stripe.StripeError as e:
                    raise StripelibError(e.message, e)
                    
            transaction.status = TRANSACTION_STATUS_COMPLETE
            transaction.pay_key = charge.id
            transaction.date_payment = now()
            transaction.save()
                
            self.charge = charge
    
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

def suite():
    
    #testcases = [PledgeScenarioTest, StripeErrorTest]
    testcases = [StripeErrorTest]
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
