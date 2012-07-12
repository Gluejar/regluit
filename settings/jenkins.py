from regluit.settings.common import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Ed Summers', 'ehs@pobox.com'),
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

TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''

# facebook auth
# you'll need to create a new Facebook application to fill in these blanks
# https://developers.facebook.com/apps/

FACEBOOK_APP_ID = ''
FACEBOOK_API_SECRET = ''

# google auth
# you'll need to create a new Google application to fill in these blanks
# https://code.google.com/apis/console/
GOOGLE_OAUTH2_CLIENT_ID = ''
GOOGLE_OAUTH2_CLIENT_SECRET = ''
GOOGLE_DISPLAY_NAME = 'unglue it!'

# you'll need to register a GoogleBooks API key
# https://code.google.com/apis/console
GOOGLE_BOOKS_API_KEY = 'AIzaSyD4CFqxbxTpSQP55q0q1uTGzLBsDki1s4E'

PAYPAL_USERNAME = ''
PAYPAL_PASSWORD =  ''
PAYPAL_SIGNATURE = ''
PAYPAL_APPID = ''

PAYPAL_ENDPOINT = 'svcs.sandbox.paypal.com' # sandbox
PAYPAL_PAYMENT_HOST = 'http://www.sandbox.paypal.com' # sandbox

PAYPAL_SANDBOX_LOGIN = ''
PAYPAL_SANDBOX_PASSWORD = ''

PAYPAL_BUYER_LOGIN =''
PAYPAL_BUYER_PASSWORD = ''

# choice of payment processor
PAYMENT_PROCESSOR = 'amazon'

BASE_URL = 'http://0.0.0.0/'
BASE_URL_SECURE = 'http://0.0.0.0/'
IPN_SECURE_URL = False

# Goodreads API
GOODREADS_API_KEY = 'w8nsFplG3HFOeOLQ7rqfQ'
GOODREADS_API_SECRET = '8Dfl7nQ28VgzJctlVwf8m7zkPaWns4j79t0G9iFxbk'

# use database as queuing service in development
BROKER_TRANSPORT = "djkombu.transport.DatabaseTransport"
INSTALLED_APPS += ("djkombu",)
