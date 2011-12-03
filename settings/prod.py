from regluit.settings.common import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Ed Summers', 'ed.summers@gmail.com'),
    ('Raymond Yee', 'rdhyee+ungluebugs@gluejar.com'),
    ('Eric Hellman', 'eric@gluejar.com'),
    ('Andromeda Yelton', 'andromeda@gluejar.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'please',
        'USER': 'please',
        'PASSWORD': 'unglueit',
        'HOST': 'gluejardb.cboagmr25pjs.us-east-1.rds.amazonaws.com',
        'PORT': '',
    }
}

TIME_ZONE = 'America/New_York'
SECRET_KEY = '_^_off!8zsj4+)%qq623m&$7_m-q$iau5le0w!mw&n5tgt#x=t'

# settings for outbout email
# if you have a gmail account you can use your email address and password

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'accounts@gluejar.com'
EMAIL_HOST_PASSWORD = '7k3sWyzHpI'
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'accounts@gluejar.com'

# googlebooks 
GOOGLE_BOOKS_API_KEY = 'AIzaSyBE36z7o6NUafIWcLEB8yk2I47-8_5y1_0'

# twitter auth
TWITTER_CONSUMER_KEY = 'sd9StEg1N1qB8gGb2GRX4A'
TWITTER_CONSUMER_SECRET = 'YSKHn8Du6EWqpcWZ6sp5tqDPvcOBXK0WJWVGWyB0'

# facebook auth
FACEBOOK_APP_ID = '242881179080779'
FACEBOOK_API_SECRET = '5eae483a0e92113d884c427b578ef23a'

# google auth
GOOGLE_OAUTH2_CLIENT_ID = '989608723367.apps.googleusercontent.com'
GOOGLE_OAUTH2_CLIENT_SECRET = '3UqalKyNynnaaarumUIWh8vS'
GOOGLE_DISPLAY_NAME = 'unglue it!'

# credentials from a sandbox account that Raymond set up.
PAYPAL_USERNAME = 'glueja_1317336101_biz_api1.gluejar.com'
PAYPAL_PASSWORD =  '1317336137'
PAYPAL_SIGNATURE = 'AHVb0D1mzGD6zdX4XtKZbH.Kd6OhALVyiJVbNReOZEfyz79AoEnQJWTR'
PAYPAL_APPID = 'APP-80W284485P519543T'  # sandbox app id -- will have to replace with production id

PAYPAL_ENDPOINT = 'svcs.sandbox.paypal.com' # sandbox
PAYPAL_PAYMENT_HOST = 'https://www.sandbox.paypal.com' # sandbox

PAYPAL_SANDBOX_LOGIN = ''
PAYPAL_SANDBOX_PASSWORD = ''

PAYPAL_BUYER_LOGIN =''
PAYPAL_BUYER_PASSWORD = ''

# in live system, replace with the real Gluejar paypal email and that for our non-profit partner
PAYPAL_GLUEJAR_EMAIL = "glueja_1317336101_biz@gluejar.com"
PAYPAL_NONPROFIT_PARTNER_EMAIL = "nppart_1318957063_per@gluejar.com"

# for test purposes have a single RH paypal email
PAYPAL_TEST_RH_EMAIL = "rh1_1317336251_biz@gluejar.com"

# Goodreads API
GOODREADS_API_KEY = "vfqIO6QAhBVvlxt6hAzZJg"
GOODREADS_API_SECRET = "57tq4MpyJ15Hgm2ToZQQFWJ7vraZzOAqHLckWRXQ"

# Freebase credentials
FREEBASE_USERNAME = ''
FREEBASE_PASSWORD = ''

# send celery log to Python logging
CELERYD_HIJACK_ROOT_LOGGER = False

# BASE_URL is a hard-coding of the domain name for site and used for PayPal IPN
# Next step to try https
BASE_URL = 'http://please.unglueit.com'

# use redis for production queue
BROKER_TRANSPORT = "redis"
BROKER_HOST = "localhost"
BROKER_PORT = 6379
BROKER_VHOST = "0"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

STATIC_ROOT = '/var/www/static'
