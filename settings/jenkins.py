# coding=utf-8
from .common import *

DEBUG = True
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG
IS_PREVIEW = False

ADMINS = (
    ('Raymond Yee', 'rdhyee+ungluebugs@gluejar.com'),
    ('Eric Hellman', 'eric@gluejar.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'regluit',
        'USER': 'regluit',
        'PASSWORD': 'regluit',
        'HOST': '',
        'PORT': '',
        'TEST_CHARSET': 'utf8',
    }
}

TIME_ZONE = 'America/New_York'

# settings for outbout email
# if you have a gmail account you can use your email address and password

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'me@gmail.com'
EMAIL_HOST_PASSWORD = 'my-password'
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'info@ebookfoundation.org'


# formerly of settings/common.py to surface old vars
# TO DO: invalidate before we open source

# for use with test google account only
GOOGLE_DISPLAY_NAME = 'Unglue.It'
REDIRECT_IS_HTTPS = False

#BASE_URL = 'http://0.0.0.0/'
BASE_URL_SECURE = 'http://0.0.0.0/'



# use database as queuing service in development
BROKER_TRANSPORT = "djkombu.transport.DatabaseTransport"
#INSTALLED_APPS += ("djkombu",)
