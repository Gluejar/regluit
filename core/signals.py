from django.db.models import get_model
from django.db.utils import DatabaseError
from django.db.models.signals import post_save
from django.contrib.auth.models import User

from social_auth.signals import pre_update
from social_auth.backends.facebook import FacebookBackend
from tastypie.models import create_api_key

import registration.signals

import logging
logger = logging.getLogger(__name__)

# get email from Facebook registration
def facebook_extra_values(sender, user, response, details, **kwargs):
    if response.get('email') is not None:
        user.email = response.get('email')
    return True

pre_update.connect(facebook_extra_values, sender=FacebookBackend)


# create Wishlist and UserProfile to associate with User
def create_user_objects(sender, created, instance, **kwargs):
    # use get_model to avoid circular import problem with models
    try:
        Wishlist = get_model('core', 'Wishlist')
        UserProfile = get_model('core', 'UserProfile')
        if created:
            Wishlist.objects.create(user=instance)
            UserProfile.objects.create(user=instance)
    except DatabaseError:
        # this can happen when creating superuser during syncdb since the
        # core_wishlist table doesn't exist yet
        return

post_save.connect(create_user_objects, sender=User)


# create API key for new User
post_save.connect(create_api_key, sender=User)

def merge_emails(sender, user, **kwargs):
    logger.info('checking %s' % user.username)
    try:
        old_user=User.objects.exclude(id=user.id).get(email=user.email)
        old_user.username=user.username
        old_user.password=user.password
        user.delete()
        old_user.save()
    except User.DoesNotExist:
        return

registration.signals.user_activated.connect(merge_emails)