from django.db.models import get_model
from django.db.utils import DatabaseError
from django.db.models.signals import post_save
from django.contrib.auth.models import User

from social_auth.signals import pre_update
from social_auth.backends.facebook import FacebookBackend


def facebook_extra_values(sender, user, response, details, **kwargs):
    if response.get('email') is not None:
        user.email = response.get('email')
    return True

pre_update.connect(facebook_extra_values, sender=FacebookBackend)


def create_wishlist(sender, created, instance, **kwargs):
    # use get_model to avoid circular import problem with models
    # this fails when a superuser is being created as part of a syncdb
    # since the database table for wishlist doesn't exist yet
    try:
        Wishlist = get_model('core', 'Wishlist')
        if created:
            Wishlist.objects.create(user=instance)
    except DatabaseError:
        return


post_save.connect(create_wishlist, sender=User)
