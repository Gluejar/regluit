from regluit.settings.common import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Ed Summers', 'ehs@pobox.com'),
    ('Raymond Yee', 'rdhyee+ungluebugs@gluejar.com'),
    ('Eric Hellman', 'eric@gluejar.com'),
    ('Andromeda Yelton', 'andromeda@gluejar.com'),
    ('Rights Admin',  'rights@gluejar.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'unglueit_dev',
        'USER': 'please',
        'PASSWORD': 'unglueit',
        'HOST': 'gluejardb.cboagmr25pjs.us-east-1.rds.amazonaws.com',
        'PORT': '',
    }
}

TIME_ZONE = 'America/New_York'
SECRET_KEY = '_^_off!8zsj4+)%qq623m&$7_m-q$iau5le0w!mw&n5tgt#x=t'

# django 
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'ed.summers@gmail.com'
EMAIL_HOST_PASSWORD = 'hvkhjwujmwzvraag'
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'info@gluejar.com'

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

PAYPAL_USERNAME = ''
PAYPAL_PASSWORD =  ''
PAYPAL_SIGNATURE = ''
PAYPAL_APPID = ''

PAYPAL_ENDPOINT = 'svcs.sandbox.paypal.com' # sandbox
PAYPAL_PAYMENT_HOST = 'https://www.sandbox.paypal.com' # sandbox

PAYPAL_SANDBOX_LOGIN = ''
PAYPAL_SANDBOX_PASSWORD = ''

PAYPAL_BUYER_LOGIN =''
PAYPAL_BUYER_PASSWORD = ''

PAYPAL_GLUEJAR_EMAIL = ""

# for test purposes have a single RH paypal email
PAYPAL_TEST_RH_EMAIL = "rh1_1317336251_biz@gluejar.com"
PAYPAL_TEST_NONPROFIT_PARTNER_EMAIL = ""

# Goodreads API
GOODREADS_API_KEY = "vfqIO6QAhBVvlxt6hAzZJg"
GOODREADS_API_SECRET = "57tq4MpyJ15Hgm2ToZQQFWJ7vraZzOAqHLckWRXQ"

# Freebase credentials
FREEBASE_USERNAME = ''
FREEBASE_PASSWORD = ''

# send celery log to Python logging
CELERYD_HIJACK_ROOT_LOGGER = False
BASE_URL = 'http://0.0.0.0/'

# use redis for production queue
BROKER_TRANSPORT = "redis"
BROKER_HOST = "localhost"
BROKER_PORT = 6379
BROKER_VHOST = "0"
