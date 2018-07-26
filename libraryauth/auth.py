import logging

import requests

from django.shortcuts import redirect
from django.utils.http import urlquote

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from social_core.pipeline.social_auth import associate_by_email
from social_core.exceptions import (AuthAlreadyAssociated, SocialAuthBaseException)
from social_django.middleware import SocialAuthExceptionMiddleware

ANONYMOUS_AVATAR = '/static/images/header/avatar.png'
(NO_AVATAR, GRAVATAR, TWITTER, FACEBOOK, PRIVATETAR) = (0, 1, 2, 3, 4)
AVATARS = (NO_AVATAR, GRAVATAR, TWITTER, FACEBOOK, PRIVATETAR)

logger = logging.getLogger(__name__)

def pic_storage_url(user, backend, url):
    pic_file_name = '/pic/{}/{}'.format(backend, user)
    # download cover image to cover_file
    try:
        r = requests.get(url)
        pic_file = ContentFile(r.content)
        content_type = r.headers.get('content-type', '')
        if u'text' in content_type:
            logger.warning('Cover return text for pic_url={}'.format(url))
            return None
        pic_file.content_type = content_type
        default_storage.save(pic_file_name, pic_file)
        return default_storage.url(pic_file_name)
    except Exception, e:
        # if there is a problem, return None for cover URL
        logger.warning('Failed to store cover for username={}'.format(user))
        return None


def selectively_associate_by_email(backend, details, user=None, *args, **kwargs):
    """
    Associate current auth with a user with the same email address in the DB.
    This pipeline entry is not 100% secure unless you know that the providers
    enabled enforce email verification on their side, otherwise a user can
    attempt to take over another user account by using the same (not validated)
    email address on some provider.

    Not using Facebook or Twitter to authenticate a user.
    """
    if backend.name  in ('twitter', 'facebook'):
        return None
    return associate_by_email(backend, details, user=None, *args, **kwargs)

def facebook_extra_values(user, extra_data):
    try:
        profile_image_url = extra_data['picture']['data']['url']
        user.profile.pic_url = pic_storage_url(user, 'facebook', profile_image_url)
        if user.profile.avatar_source is None or user.profile.avatar_source is PRIVATETAR:
            user.profile.avatar_source = FACEBOOK
        user.profile.save()
        return True
    except Exception, e:
        logger.exception(e)
        return

def twitter_extra_values(user, extra_data):
    try:
        twitter_id = extra_data.get('screen_name')
        profile_image_url = extra_data.get('profile_image_url_https')
        user.profile.twitter_id = twitter_id
        if user.profile.avatar_source is None or user.profile.avatar_source in (TWITTER, PRIVATETAR):
            user.profile.pic_url = pic_storage_url(user, 'twitter', profile_image_url)
        if user.profile.avatar_source is None or user.profile.avatar_source is PRIVATETAR:
            user.profile.avatar_source = TWITTER
        user.profile.save()
        return True
    except Exception, e:
        logger.error(e)
        return False

def deliver_extra_data(backend, user, social, response, *args, **kwargs):
    if backend.name == 'twitter':
        twitter_extra_values(user, social.extra_data)
    if backend.name == 'facebook':
        facebook_extra_values(user, response)

# following is needed because of length limitations in a unique constrain for MySQL
def chop_username(username, *args, **kwargs):
    if username and len(username) > 222:
        return {'username':username[0:222]}

def selective_social_user(backend, uid, user=None, *args, **kwargs):
    provider = backend.name
    social = backend.strategy.storage.user.get_social_auth(provider, uid)
    if social:
        if user and social.user != user:
            if backend.name not in ('twitter', 'facebook'):
                msg = 'This {0} account is already in use.'.format(provider)
                raise AuthAlreadyAssociated(backend, msg)
        elif not user:
            user = social.user
    return {'social': social,
            'user': user,
            'is_new': user is None,
            'new_association': False}

# https://stackoverflow.com/a/19361220
# adapting https://github.com/omab/python-social-auth/blob/v0.2.10/social/apps/django_app/middleware.py#L25

class SocialAuthExceptionMiddlewareWithoutMessages(SocialAuthExceptionMiddleware):
    """
    a modification of SocialAuthExceptionMiddleware to pass backend and message without
    attempting django.messages
    """
    def process_exception(self, request, exception):

        if isinstance(exception, SocialAuthBaseException):
            backend = getattr(request, 'backend', None)
            backend_name = getattr(backend, 'name', 'unknown-backend')

            message = self.get_message(request, exception)
            logger.warning(message)

            url = self.get_redirect_uri(request, exception)
            url += ('?' in url and '&' or '?') + \
                   'message={0}&backend={1}'.format(urlquote(message),
                                                    backend_name)
            return redirect(url)
