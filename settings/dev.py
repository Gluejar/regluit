from regluit.settings.common import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# if you're doing development work, you'll want this to be zero
IS_PREVIEW = False

# SITE_ID for your particular site -- must be configured in /core/fixtures/initial_data.json
SITE_ID = 3

ADMINS = (
    ('Raymond Yee', 'rdhyee+ungluebugs@gluejar.com'),
    ('Eric Hellman', 'eric@gluejar.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'regluit.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'TEST_CHARSET': 'utf8',
    }
}

TIME_ZONE = 'America/New_York'
SECRET_KEY = '_^_off!8zsj4+)%qq623m&$7_m-q$iau5le0w!mw&n5tgt#x=t'

# settings for outbout email
# if you have a gmail account you can use your email address and password

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'me@gmail.com'
EMAIL_HOST_PASSWORD = 'my-password'
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'info@gluejar.com'

# twitter auth
# you'll need to create a new Twitter application to fill in these blanks
# https://dev.twitter.com/apps/new

SOCIAL_AUTH_TWITTER_KEY = ''
SOCIAL_AUTH_TWITTER_SECRET = ''

# facebook auth
# you'll need to create a new Facebook application to fill in these blanks
# https://developers.facebook.com/apps/

SOCIAL_AUTH_FACEBOOK_KEY = ''
SOCIAL_AUTH_FACEBOOK_SECRET = ''

# get these (as oauth2 client ID and Secret from 
# https://console.developers.google.com/project/569579163337/apiui/credential?authuser=1
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = ''
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ''


# you'll need to register a GoogleBooks API key
# https://code.google.com/apis/console
GOOGLE_BOOKS_API_KEY = ''

# Payment processor switch
PAYMENT_PROCESSOR = 'stripelib'

# set -- sandbox or production Amazon FPS?
AMAZON_FPS_HOST = "fps.sandbox.amazonaws.com"
#AMAZON_FPS_HOST = "fps.amazonaws.com"


#BASE_URL = 'http://0.0.0.0'
BASE_URL_SECURE = 'https://0.0.0.0' 
IPN_SECURE_URL = True

# use database as queuing service in development
BROKER_TRANSPORT = "djkombu.transport.DatabaseTransport"
INSTALLED_APPS += ("djkombu",)

# Goodreads API
GOODREADS_API_KEY = ''
GOODREADS_API_SECRET = ''

# LibraryThing API
LIBRARYTHING_API_KEY = ''

# Freebase credentials
FREEBASE_USERNAME = ''
FREEBASE_PASSWORD = ''

# send celery log to Python logging
CELERYD_HIJACK_ROOT_LOGGER = False

# a debug_toolbar setting
INTERNAL_IPS = ('127.0.0.1',)

CELERYD_LOG_LEVEL = "INFO"

#  an optional setting to change regluit.utils.localdatetime._now -- setting it to None will cause
#  a default _now() to be computed in regluit.utils.localdatetime

LOCALDATETIME_NOW = None

# selenium-related testing parameters
# in Django 1.4, we'll get a URL for LiveServerTestCase https://docs.djangoproject.com/en/dev/topics/testing/#django.test.LiveServerTestCase
# but for now, we would have to manually configure our own test server.
LIVE_SERVER_TEST_URL = "http://127.0.0.1:8000"

# username, password to pass to LIVE_SERVER_TEST_URL

UNGLUEIT_TEST_USER = None
UNGLUEIT_TEST_PASSWORD = None

# local settings for maintenance mode
MAINTENANCE_MODE = False

# decide which of the period tasks to add to the schedule
#CELERYBEAT_SCHEDULE['send_test_email'] = SEND_TEST_EMAIL_JOB
#CELERYBEAT_SCHEDULE['emit_notifications'] = EMIT_NOTIFICATIONS_JOB
CELERYBEAT_SCHEDULE['report_new_ebooks'] = EBOOK_NOTIFICATIONS_JOB

try:
    from regluit.settings.local import *
except ImportError:
    pass