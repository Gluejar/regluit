import stripe

# if customer.id doesn't exist, create one and then charge the customer
# we probably should ask our users whether they are ok with our creating a customer id account -- or ask for credit
# card info each time....

# should load the keys for Stripe from db -- but for now just hardcode here
try:
    from regluit.core.models import Key
    STRIPE_PK = Key.objects.get(name="STRIPE_PK").value
    STRIPE_SK = Key.objects.get(name="STRIPE_SK").value
    STRIPE_PARTNER_PK = Key.objects.get(name="STRIPE_PARTNER_PK").value
    STRIPE_PARTNER_SK = Key.objects.get(name="STRIPE_PARTNER_SK").value    
    logger.info('Successful loading of STRIPE_*_KEYs')
except Exception, e:
    STRIPE_PK = 'pk_0EajXPn195ZdF7Gt7pCxsqRhNN5BF'
    STRIPE_SK = 'sk_0EajIO4Dnh646KPIgLWGcO10f9qnH'
    STRIPE_PARTNER_PK ='pk_0AnIkNu4WRiJYzxMKgruiUwxzXP2T'
    STRIPE_PARTNER_SK = 'sk_0AnIvBrnrJoFpfD3YmQBVZuTUAbjs'
    
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

ERROR_TESTING = (
    ('ADDRESS1_ZIP_FAIL', '4000000000000010', 'address_line1_check and address_zip_check will both fail'),
    ('ADDRESS1_FAIL', '4000000000000028', 'address_line1_check will fail.'),
    ('ADDRESS_ZIP_FAIL', '4000000000000036', 'address_zip_check will fail.'),
    ('CVC_CHECK_FAIL', '4000000000000101', 'cvc_check will fail.'),
    ('CHARGE_FAIL', '4000000000000341', 'Attaching this card to a Customer object will succeed, but attempts to charge the customer will fail.'),
    ('CHARGE_DECLINE', '4000000000000002', 'Charges with this card will always be declined.')
)

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
    # customer or card required but not both
    # charge the Customer instead of the card
    # amount in cents
        charge = stripe.Charge(api_key=self.api_key).create(
            amount=int(100*amount), # in cents
            currency=currency,
            customer=customer.id,
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
   
 
# key entities:  Charge, Customer, Token, Event
# IPNs/webhooks: https://stripe.com/docs/webhooks

# charge object: https://stripe.com/docs/api?lang=python#charge_object
# need to study to figure out db schema

# all events
# https://stripe.com/docs/api?lang=python#list_events
