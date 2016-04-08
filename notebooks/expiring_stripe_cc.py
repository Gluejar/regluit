# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# # working out logic around expiring credit cards

# <codecell>

from regluit.payment.stripelib import StripeClient
from regluit.payment.models import Account

from django.db.models import Q, F

# <codecell>

# use the localdatetime?

from regluit.utils import localdatetime
localdatetime.date_today()

# <headingcell level=2>

# expiring, expired, soon to expire cards

# <codecell>

from regluit.payment.models import Account
from django.db.models import Q
import datetime
from dateutil.relativedelta import relativedelta


# set the month/year for comparison

# # http://stackoverflow.com/a/15155212/7782
today = datetime.date.today()
year = today.year
month = today.month

date_before_month = today + relativedelta(months=-1)
year_last_month = date_before_month.year
month_last_month = date_before_month.month


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

# <codecell>

# looking at filtering Accounts that might expire

# if the the month of the expiration date  == next month or earlier 
# accounts with expiration of this month and last month -- and to be more expansive filter:  expiration with this month or before
# also Account.objects.filter(Q(date_deactivated__isnull=True))
# 
# accounts_expired = active_accounts.filter((Q(card_exp_year__lt=year) | Q(card_exp_year=year, card_exp_month__lt = month)))

accounts_to_consider_expansive = Account.objects.filter(Q(date_deactivated__isnull=True)).filter((Q(card_exp_year__lt=year) | Q(card_exp_year=year, card_exp_month__lte = month)))

# this month or last last monthj
accounts_to_consider_narrow = Account.objects.filter(Q(date_deactivated__isnull=True)).filter(Q(card_exp_year=year, card_exp_month = month) | Q(card_exp_year=year_last_month, card_exp_month = month_last_month))

for account in accounts_to_consider_narrow:
    print (account.user, account.card_exp_month, account.card_exp_year) 

# <codecell>

from regluit.utils.localdatetime import date_today

today = date_today()
year = today.year
month = today.month
accounts_to_calc = Account.objects.filter(Q(date_deactivated__isnull=True)).filter((Q(card_exp_year__lt=year) | Q(card_exp_year=year, card_exp_month__lte = month)))
accounts_to_calc

# <codecell>

from regluit.payment import tasks
k = tasks.update_account_status.apply(args=[False])

# <codecell>

k.get()

# <codecell>

# list any active transactions tied to users w/ expiring and expired CC?

print [(account.user, account.user.email, [t.campaign for t in account.user.transaction_set.filter(status='ACTIVE')]) for account in accounts_expiring]
print [(account.user, account.user.email, [t.campaign for t in account.user.transaction_set.filter(status='ACTIVE')]) for account in accounts_expired]

# <codecell>

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

# <codecell>

Account.objects.filter(status='EXPIRED')

# <headingcell level=1>

# coming up with good notices to send out 

# <codecell>

from notification.engine import send_all
from notification import models as notification

from django.contrib.sites.models import Site

# <codecell>

from django.contrib.auth.models import User
from django.conf import settings
me = User.objects.get(email = settings.EMAIL_HOST_USER )

# <codecell>

print me, settings.EMAIL_HOST

# <codecell>

notification.send_now([me], "account_expiring", {
                    'user': me, 
                    'site':Site.objects.get_current()
                }, True)

# <codecell>

notification.send_now([me], "account_expired", {
                    'user': me, 
                    'site':Site.objects.get_current()
                }, True)

# <headingcell level=1>

# accounts with problem transactions

# <codecell>

# easy to figure out the card used for a specific problem transaction?
# want to figure out problem status for a given Account

from regluit.payment.models import Transaction

# Account has fingerprint
# transaction doesn't have fingerprint -- will have to calculate fingerprint of card associated with transaction
# w/ error if we store pay_key -- any problem?

Transaction.objects.filter(host='stripelib', status='Error', approved=True).count()

# <markdowncell>

# I am hoping that we can use the API to ask for a list of charge.failed --> but I don't see a way to query charges based  upon on the status of the charges --  what you have to iterate through all of the charges and filter based on status.  ( maybe I should confirm this fact with people at  stripe) -- ok  let's do  that for now.
# 
# **Note:  One needs to have productionstripe keys loaded in database to run following code**
# 
# What script do I run to load these keys? 
# 
# `/Volumes/ryvault1/gluejar/stripe/set_stripe_keys.py`

# <codecell>

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

# <headingcell level=2>

# Work to create an Account.account_status()

# <markdowncell>

# First working out conditions for **ERROR** status

# <codecell>

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

# <markdowncell>

# https://github.com/Gluejar/regluit/commit/c3f922e9ba61bc412657cfa18c7d8f8d3df6eb38#L1R341 --> it's made its way into the unglue.it code, at least in the `expiring_cc` branch

# <codecell>

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
    

# <codecell>

# test out with the account that is currently erroring out

acc_with_error = Transaction.objects.get(id=773).user.profile.account
print account_status(acc_with_error)
print
acc_with_error.status

# <markdowncell>

# # validity of accounts -- need to use real stripe keys if we want to look at production data

# <codecell>

from regluit.payment.stripelib import StripeClient
from django.db.models import Q

sc = StripeClient()
customers = list(sc._all_objs('Customer'))

# 3 checks available to us:  Address Line 1, zip code, CVC

[(customer.id, customer.description, customer.active_card.get("address_line1_check"), 
customer.active_card.get("address_zip_check"), 
customer.active_card.get("cvc_check")) for customer in customers if customer.active_card is not None]

# <markdowncell>

# # look at only customers that are attached to active Account

# <codecell>

from regluit.payment.stripelib import StripeClient
from regluit.payment.models import Account

sc = StripeClient()
customers = sc._all_objs('Customer')

active_accounts = Account.objects.filter(Q(date_deactivated__isnull=True))

active_customer_ids = set([account.account_id for account in active_accounts])

# <codecell>

[(customer.active_card["address_line1_check"], 
customer.active_card["address_zip_check"], 
customer.active_card["cvc_check"]) for customer in customers if customer.id in active_customer_ids]

# <markdowncell>

# # handling campaign totals properly based on account statuses
# 
# **Will we need to start marking accounts as expired explicitly?** 
# 
# add a manager method?

# <codecell>

# calculate which active transactions not tied to an active account w/ unexpired CC

# <markdowncell>

# # should we delete stripe accounts associated with deactivated accounts -- I think yes
# 
# How to do?  
# 
# * clean up Customer associated with current deactivated accounts
# * build logic in to delete Customer once the correspending account are deactivated and we safely have a new Account/Customer in place -- maybe a good task to put into the webhook handler

# <codecell>

len(active_customer_ids)

# <codecell>

# do the users w/ deactivated accounts have active ones?

