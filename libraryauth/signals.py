import logging
import registration.signals
from django.contrib.auth.models import User
from django.dispatch import receiver

logger = logging.getLogger(__name__)

@receiver(registration.signals.user_activated)
def handle_same_email_account(sender, user, **kwargs):
    logger.info('checking %s' % user.username)
    old_users = User.objects.exclude(id=user.id).filter(email=user.email)
    for old_user in old_users:
        # decide why there's a previous user with this email
        if not old_user.is_active:
            # never activated
            old_user.delete()
        elif old_user.date_joined < user.date_joined:
            # relax
            pass
        else:
            # shouldn't happen; don't want to delete the user
            # in case the user is being used for something
            old_user.email = '%s.unglue.it'% old_user.email

