from notification import models as notification

from django.dispatch import Signal

transaction_charged = Signal(providing_args=["transaction"])
transaction_failed = Signal(providing_args=["transaction"])
transaction_refunded = Signal(providing_args=["transaction"])
transaction_disputed = Signal(providing_args=["transaction"])

pledge_created = Signal(providing_args=["transaction"]) # should really be called "authorization created
pledge_modified = Signal(providing_args=["transaction", "up_or_down"])
credit_balance_added = Signal(providing_args=["amount"])

from django.db.models.signals import post_save
from django.db.utils import DatabaseError
from django.db.models import get_model
from django.contrib.auth.models import User

# create Credit to associate with User
def create_user_objects(sender, created, instance, **kwargs):
    # use get_model to avoid circular import problem with models
    # don't create Credit if we are loading fixtures http://stackoverflow.com/a/3500009/7782
    if not kwargs.get('raw', False):
        try:
            Credit = get_model('payment', 'Credit')
            if created:
                Credit.objects.create(user=instance)
        except DatabaseError:
            # this can happen when creating superuser during syncdb since the
            # core_wishlist table doesn't exist yet
            return

post_save.connect(create_user_objects, sender=User)

def handle_credit_balance(sender, amount=0, **kwargs):
    notification.queue([sender.user], "pledge_donation_credit", {
            'user':sender.user,
            'amount':amount,
            'minus_amount':-amount
        }, True)
    from regluit.core.tasks import emit_notifications
    emit_notifications.delay()
    
# successful_campaign -> send notices    
credit_balance_added.connect(handle_credit_balance)