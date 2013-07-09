
# # working out logic around expiring credit cards

# In[ ]:
from regluit.payment.stripelib import StripeClient
from regluit.payment.models import Account

from django.db.models import Q, F


### expiring, expired, soon to expire cards

# In[ ]:
from regluit.payment.models import Account
from django.db.models import Q
import datetime

# set the month/year for comparison

#
today = datetime.date.today()
year = today.year
month = today.month

#year = 2013
#month = 2

# look only at active accounts

active_accounts = Account.objects.filter(Q(date_deactivated__isnull=True))

# calculate expired cards
accounts_expired = active_accounts.filter((Q(card_exp_year__lt=year) | Q(card_exp_year=year, card_exp_month__lt = month)))

# expiring on a given month

accounts_expiring = active_accounts.filter(card_exp_year=year, card_exp_month = month)

# yet to expire

accounts_expiring_later = active_accounts.filter((Q(card_exp_year__gt=year) | Q(card_exp_year=year, card_exp_month__gt = month)))

print "number of active accounts", active_accounts.count()
print "expired: {0} expiring: {1} expire later: {2}".format(accounts_expired.count(), accounts_expiring.count(), accounts_expiring_later.count())

# expiring soon
print "expiring soon"
print [(account.user, account.card_exp_month, account.card_exp_year) for account in accounts_expiring]

# expired
print "expired"
print [(account.user, account.card_exp_month, account.card_exp_year) for account in accounts_expired]

# In[ ]:
# list any active transactions tied to users w/ expiring and expired CC?

print [(account.user, account.user.email, [t.campaign for t in account.user.transaction_set.filter(status='ACTIVE')]) for account in accounts_expiring]
print [(account.user, account.user.email, [t.campaign for t in account.user.transaction_set.filter(status='ACTIVE')]) for account in accounts_expired]

# In[ ]:
# more to the point, what cards have expired or will expire by the time we have a hopefully 
# successful close for Feeding the City (campaign # 15)?

from django.contrib.auth.models import User
from regluit.core.models import Campaign

ftc_campaign = Campaign.objects.get(id=15)

# get all accounts tied to this campaign....
len(ftc_campaign.supporters())

ftc_expired_accounts = [User.objects.get(id=supporter_id).profile.account for supporter_id in ftc_campaign.supporters()
    if User.objects.get(id=supporter_id).profile.account.status == 'EXPIRED' or 
       User.objects.get(id=supporter_id).profile.account.status == 'EXPIRING']
ftc_expired_accounts


# In[ ]:
Account.objects.filter(status='EXPIRED')

## coming up with good notices to send out 

# In[ ]:
from notification.engine import send_all
from notification import models as notification

from django.contrib.sites.models import Site

# In[ ]:
from django.contrib.auth.models import User
ry = User.objects.get(email = 'raymond.yee@gmail.com')

# In[ ]:
notification.send_now([ry], "account_expiring", {
                    'user': ry, 
                    'site':Site.objects.get_current()
                }, True)

# In[ ]:
notification.send_now([ry], "account_expired", {
                    'user': ry, 
                    'site':Site.objects.get_current()
                }, True)

## accounts with problem transactions

# In[ ]:
# easy to figure out the card used for a specific problem transaction?
# want to figure out problem status for a given Account

from regluit.payment.models import Transaction

# Account has fingerprint
# transaction doesn't have fingerprint -- will have to calculate fingerprint of card associated with transaction
# w/ error if we store pay_key -- any problem?

Transaction.objects.filter(host='stripelib', status='Error', approved=True).count()

# I am hoping that we can use the API to ask for a list of charge.failed --> but I don't see a way to query charges based  upon on the status of the charges --  what you have to iterate through all of the charges and filter based on status.  ( maybe I should confirm this fact with people at  stripe) -- ok  let's do  that for now.
# 
# **Note:  One needs to have productionstripe keys loaded in database to run following code**
# 
# What script do I run to load these keys? 
# 
# `/Volumes/ryvault1/gluejar/stripe/set_stripe_keys.py`

# In[ ]:
from regluit.payment.stripelib import StripeClient
from regluit.payment.models import Transaction

import json
from itertools import islice

sc = StripeClient()
charges = islice(sc._all_objs('Charge'), None)

failed_charges = [(c.amount, c.id, c.failure_message, json.loads(c.description)['t.id']) for c in charges if c.failure_message is not None]
print failed_charges

# look up corresponding Transactions  and  flag the ones that have not been properly charged

print [t.status for t in Transaction.objects.filter(id__in = [fc[3] for fc in failed_charges])]


### Work to create an Account.account_status()

# First working out conditions for **ERROR** status

# In[ ]:
# acc_with_error = transaction # 773 -- the one with an Error that we wrote off

acc_with_error = Transaction.objects.get(id=773).user.profile.account
acc_with_error.user

# trans is all stripe transactions of user associated w/ acc_with_error

trans = Transaction.objects.filter(host='stripelib', 
             status='Error', approved=True, user=acc_with_error.user)

# comparing the transaction payment date with when account created.
# why? 
# if account created after transaction payment date, we would want to retry the payment.


acc_with_error.date_created, [t.date_payment for t in trans] 

print trans.filter(date_payment__gt=acc_with_error.date_created)

# https://github.com/Gluejar/regluit/commit/c3f922e9ba61bc412657cfa18c7d8f8d3df6eb38#L1R341 --> it's made its way into the unglue.it code, at least in the `expiring_cc` branch

# In[ ]:
# Given the specific account I would like to cut the status... need to handle expiration as well as  declined charges

from regluit.payment.models import Transaction
from regluit.payment.models import Account
from regluit.utils.localdatetime import now, date_today

from itertools import islice

def account_status(account):

# is it deactivated?

    today = date_today()
    transactions_w_error_status_older_account = Transaction.objects.filter(host='stripelib', 
             status='Error', approved=True, user=account.user)
    
    if account.date_deactivated is not None:
        return 'DEACTIVATED'

# is it expired?

    elif account.card_exp_year < today.year or (account.card_exp_year == today.year and account.card_exp_month < today.month):
        return 'EXPIRED'
    
# about to expire?  do I want to distinguish from 'ACTIVE'?

    elif (account.card_exp_year == today.year and account.card_exp_month == today.month):
        return 'EXPIRING'        

# any transactions w/ errors after the account date?
# Transaction.objects.filter(host='stripelib', status='Error', approved=True).count()

    elif Transaction.objects.filter(host='stripelib', 
             status='Error', approved=True, user=account.user).filter(date_payment__gt=account.date_created):
        return 'ERROR'
    else:
        return 'ACTIVE'
    

# In[ ]:
# test out with the account that is currently erroring out

acc_with_error = Transaction.objects.get(id=773).user.profile.account
print account_status(acc_with_error)
print
acc_with_error.status

# # validity of accounts -- need to use real stripe keys if we want to look at production data

# In[ ]:
from regluit.payment.stripelib import StripeClient
from django.db.models import Q

sc = StripeClient()
customers = list(sc._all_objs('Customer'))

# 3 checks available to us:  Address Line 1, zip code, CVC

[(customer.id, customer.description, customer.active_card.get("address_line1_check"), 
customer.active_card.get("address_zip_check"), 
customer.active_card.get("cvc_check")) for customer in customers if customer.active_card is not None]


# # look at only customers that are attached to active Account

# In[ ]:
from regluit.payment.stripelib import StripeClient
from regluit.payment.models import Account

sc = StripeClient()
customers = sc._all_objs('Customer')

active_accounts = Account.objects.filter(Q(date_deactivated__isnull=True))

active_customer_ids = set([account.account_id for account in active_accounts])


# In[ ]:
[(customer.active_card["address_line1_check"], 
customer.active_card["address_zip_check"], 
customer.active_card["cvc_check"]) for customer in customers if customer.id in active_customer_ids]

# # handling campaign totals properly based on account statuses
# 
# **Will we need to start marking accounts as expired explicitly?** 
# 
# add a manager method?
# 

# In[ ]:
# calculate which active transactions not tied to an active account w/ unexpired CC


# # should we delete stripe accounts associated with deactivated accounts -- I think yes
# 
# How to do?  
# 
# * clean up Customer associated with current deactivated accounts
# * build logic in to delete Customer once the correspending account are deactivated and we safely have a new Account/Customer in place -- maybe a good task to put into the webhook handler

# In[ ]:
len(active_customer_ids)

# In[ ]:
# do the users w/ deactivated accounts have active ones?
