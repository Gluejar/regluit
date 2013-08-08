"""
external library imports
"""
from celery.task import task

"""
django imports
"""
from django.contrib.sites.models import Site
from django.db.models import Q

from notification import models as notification

"""
regluit imports
"""
from regluit.payment.models import Account
from regluit.utils.localdatetime import date_today

#task to update the status of accounts
@task
def update_account_status(all_accounts=True, send_notice_on_change_only=True):
    """update the status of all Accounts
    
        By default, send notices only if the status is *changing*.  Set send_notice_on_change_only = False to
        send notice based on new_status regardless of old status.  (Useful for initialization)
    """
    errors = []
    
    if all_accounts:
        accounts_to_calc = Account.objects.all()
    else:
        # active accounts with expiration dates from this month earlier
        today = date_today()
        year = today.year
        month = today.month
        accounts_to_calc = Account.objects.filter(Q(date_deactivated__isnull=True)).filter((Q(card_exp_year__lt=year) | Q(card_exp_year=year, card_exp_month__lte = month)))
    
    for account in accounts_to_calc:
        try:
            account.update_status(send_notice_on_change_only=send_notice_on_change_only)
        except Exception, e:
            errors.append(e)

    # fire off notices
    
    from regluit.core.tasks import emit_notifications
    emit_notifications.delay()   

    return errors
 
# task run roughly 8 days ahead of card expirations
@task
def notify_expiring_accounts():    
    expiring_accounts = Account.objects.filter(status='EXPIRING')
    for account in expiring_accounts:
        notification.send_now([account.user], "account_expiring", {
                    'user': account.user,
                    'site':Site.objects.get_current()
                }, True)

# used for bootstrapping our expired cc notification for first time
@task
def notify_expired_accounts():
    expired_accounts = Account.objects.filter(status='EXPIRED')
    for account in expired_accounts:
        notification.send_now([account.user], "account_expired", {
                    'user': account.user,
                    'site':Site.objects.get_current()
                }, True)

