import stripe

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
    STRIPE_PARTNER_PK = None
    STRIPE_PARTNER_SK = None
    
stripe.api_key =  STRIPE_SK   
    
# if you create a Customer object, then you'll be able to charge multiple times. You can create a customer with a token.

# https://stripe.com/docs/tutorials/charges

def create_customer (card=None, description=None, email=None, account_balance=None, plan=None, trial_end=None):
    """card is a dictionary or a token"""
    # https://stripe.com/docs/api?lang=python#create_customer

    customer = stripe.Customer.create(
        card=card,
        description=description,
        email=email,
        account_balance=account_balance,
        plan=plan,
        trial_end=trial_end
    )
    
    # customer.id is useful to save in db
    return customer

# if customer.id doesn't exist, create one and then charge the customer
# we probably should ask our users whether they are ok with our creating a customer id account -- or ask for credit
# card info each time....

def create_charge(amount, currency="usd", customer=None, card=None, description=None ):
# https://stripe.com/docs/api?lang=python#create_charge
# customer or card required but not both
# charge the Customer instead of the card
# amount in cents
    charge = stripe.Charge.create(
        amount=int(100*amount), # in cents
        currency=currency,
        customer=customer.id,
        description=description
    )
    
    return charge

def refund_charge(id):
    # https://stripe.com/docs/api?lang=python#refund_charge
    ch = stripe.Charge.retrieve(id)
    ch.refund()
    return ch

def list_all_charges(count=None, offset=None, customer=None):
    # https://stripe.com/docs/api?lang=python#list_charges
    return stripe.Charge.all(count=count, offset=offset, customer=customer)
    
# key entities:  Charge, Customer, Token, Event
# IPNs/webhooks: https://stripe.com/docs/webhooks

# charge object: https://stripe.com/docs/api?lang=python#charge_object
# need to study to figure out db schema

# all events
# https://stripe.com/docs/api?lang=python#list_events
