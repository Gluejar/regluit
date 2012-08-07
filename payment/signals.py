from django.dispatch import Signal

transaction_charged = Signal(providing_args=["transaction"])
pledge_created = Signal(providing_args=["transaction"])
pledge_modified = Signal(providing_args=["transaction", "up_or_down"])

from django.db.models.signals import post_save
from django.db.utils import DatabaseError
from django.db.models import get_model
from django.contrib.auth.models import User

# create Credit to associate with User
def create_user_objects(sender, created, instance, **kwargs):
    # use get_model to avoid circular import problem with models
    try:
        Credit = get_model('payment', 'Credit')
        if created:
            Credit.objects.create(user=instance)
    except DatabaseError:
        # this can happen when creating superuser during syncdb since the
        # core_wishlist table doesn't exist yet
        return

post_save.connect(create_user_objects, sender=User)
