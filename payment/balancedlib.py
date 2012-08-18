import balanced

# should load the keys for balanced from db -- but for now just hardcode here
try:
    from regluit.core.models import Key
    BALANCED_SK = Key.objects.get(name="BALANCED_SK").value
    logger.info('Successful loading of STRIPE_*_KEYs')
except Exception, e:
    # for unglue.it TEST app
    BALANCED_SK = 'd3a17790e88411e1ac62026ba7e239a9'
    
# set up with our key    
balanced.configure(BALANCED_SK)
MARKETPLACE_URI = balanced.Marketplace.my_marketplace.uri


"""
from regluit.payment import balancedlib
from regluit.payment.balancedlib import balanced

mp = balanced.Marketplace.my_marketplace
mp.domain_url

# create a card and associated buyer

card = balanced.Card(
    card_number="5105105105105100",
    expiration_month="12",
    expiration_year="2015",
    ).save()

buyer = mp.create_buyer("buyer@example.org", card.uri)
"""


# https://github.com/balanced/balanced-python/blob/master/examples/examples.py

def attach_card_to_buyer(card_uri, buyer_email):
    
    # for a new account
    try:
        buyer = balanced.Marketplace.my_marketplace.create_buyer(
            email_address, card_uri=card_uri)
    except balanced.exc.HTTPError as ex:
        if ex.category_code == 'duplicate-email-address':
            buyer = balanced.Account.query.filter(email_address=email_address)[0]
            buyer.add_card(card_uri)
        else:
            # TODO: handle 400 or 409 errors
            raise
        
def escrow(amount, buyer, appears_on_statement_as=''):
    
    amount_in_cents = 10 * 100  # $10.00 USD
    debit = buyer.debit(amount_in_cents, appears_on_statement_as=appears_on_statement_as)
    return debit
    # All debits are implicitly escrowed within your marketplace until you choose to create a credit to pay a merchant.
    
def credit(amount, merchant, appears_on_statement_as=''):
    amount_in_cents = amount * 100  # $9.00 USD
    merchant.credit(amount_in_cents, appears_on_statement_as=appears_on_statement_as)
    
"""

# entities that can be created from Marketplace: buyer, merchant, card, bank_account

mp.create_buyer(email_address, card_uri, name=None, meta=None)
mp.create_card(name, card_number, expiration_month, expiration_year, security_code=None, street_address=None, city=None, region=None, postal_code=None, country_code=None, phone_number=None)
mp.create_merchant(email_address, merchant=None, bank_account_uri=None, name=None, meta=None, merchant_uri=None)
mp.create_bank_account(name, account_number, bank_code)


"""