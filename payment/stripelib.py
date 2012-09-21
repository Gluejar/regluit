# https://github.com/stripe/stripe-python
# https://stripe.com/docs/api?lang=python#top

from datetime import datetime
from pytz import utc

from regluit.payment.parameters import PAYMENT_HOST_STRIPE
from regluit.payment.parameters import TRANSACTION_STATUS_COMPLETE
from regluit.payment.baseprocessor import BasePaymentRequest
from regluit.utils.localdatetime import now, zuluformat

import stripe

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
    STRIPE_PARTNER_PK = Key.objects.get(name="STRIPE_PARTNER_PK").value
    STRIPE_PARTNER_SK = Key.objects.get(name="STRIPE_PARTNER_SK").value    
    logger.info('Successful loading of STRIPE_*_KEYs')
except Exception, e:
    # currently test keys for Gluejar and for raymond.yee@gmail.com as standin for non-profit
    STRIPE_PK = 'pk_0EajXPn195ZdF7Gt7pCxsqRhNN5BF'
    STRIPE_SK = 'sk_0EajIO4Dnh646KPIgLWGcO10f9qnH'
    STRIPE_PARTNER_PK ='pk_0AnIkNu4WRiJYzxMKgruiUwxzXP2T'
    STRIPE_PARTNER_SK = 'sk_0AnIvBrnrJoFpfD3YmQBVZuTUAbjs'
    
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

# types of errors / when they can be handled

#card_declined: Use this special card number - 4000000000000002.
#incorrect_number: Use a number that fails the Luhn check, e.g. 4242424242424241.
#invalid_expiry_month: Use an invalid month e.g. 13.
#invalid_expiry_year: Use a year in the past e.g. 1970.
#invalid_cvc: Use a two digit number e.g. 99.


def filter_none(d):
    return dict([(k,v) for (k,v) in d.items() if v is not None])
    
# if you create a Customer object, then you'll be able to charge multiple times. You can create a customer with a token.

# https://stripe.com/docs/tutorials/charges

def card (number=TEST_CARDS[0][0], exp_month='01', exp_year='2020', cvc=None, name=None,
          address_line1=None, address_line2=None, address_zip=None, address_state=None, address_country=None):
    
    card = {
        "number": number,
        "exp_month": str(exp_month),
        "exp_year": str(exp_year),
        "cvc": str(cvc) if cvc is not None else None,
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

    def create_customer (self, card=None, description=None, email=None, account_balance=None, plan=None, trial_end=None):
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
   
# what to work through?

# can't test Transfer in test mode: "There are no transfers in test mode."

#pledge scenario
# bad card -- what types of erros to handle?
# https://stripe.com/docs/api#errors

# what errors are handled in the python library and how?
# 

# Account?

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

class StripePaymentRequest(BasePaymentRequest):
    pass

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
        if transaction.preapproval_key.startswith('cus_'):
            charge = sc.create_charge(transaction.amount, customer=transaction.preapproval_key, description="${0} for test / retain cc".format(transaction.amount))
        elif transaction.preapproval_key.startswith('tok_'):
            charge = sc.create_charge(transaction.amount, card=transaction.preapproval_key, description="${0} for test / cc not retained".format(transaction.amount))

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
    


def suite():
    
    testcases = [PledgeScenarioTest]
    #testcases = []
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
