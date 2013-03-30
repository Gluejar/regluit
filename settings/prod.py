from regluit.settings.common import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG
# we are launched!
IS_PREVIEW = False

SITE_ID = 1

ADMINS = (
    ('Raymond Yee', 'rdhyee+ungluebugs@gluejar.com'),
    ('Eric Hellman', 'eric@gluejar.com'),
    ('Andromeda Yelton', 'andromeda@gluejar.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'unglueit',
        'USER': 'root',
        'PASSWORD': 'unglue1t',
        'HOST': 'production.cboagmr25pjs.us-east-1.rds.amazonaws.com',
        'PORT': '',
        'TEST_CHARSET': 'utf8',
    }
}

TIME_ZONE = 'America/New_York'
SECRET_KEY = '_^_off!8zsj4+)%qq623m&$7_m-q$iau5le0w!mw&n5tgt#x=t'

# settings for outbout email
# if you have a gmail account you can use your email address and password

#EMAIL_USE_TLS = True
#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_HOST_USER = 'accounts@gluejar.com'
#EMAIL_HOST_PASSWORD = '7k3sWyzHpI'
#EMAIL_PORT = 587
#DEFAULT_FROM_EMAIL = 'accounts@gluejar.com'

# testing out using Amazon SES

EMAIL_BACKEND = 'django_smtp_ssl.SSLEmailBackend'
MAIL_USE_TLS = True 
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_HOST_USER = 'AKIAJXM4QX324HXCH54Q'
EMAIL_HOST_PASSWORD = 'AgR9hVmSSOhetuLOnbFEFo9PTnL9iAM/52NOPGkS3Rwh'
EMAIL_PORT = 465
DEFAULT_FROM_EMAIL = 'notices@gluejar.com'

# googlebooks 
GOOGLE_BOOKS_API_KEY = 'AIzaSyBE36z7o6NUafIWcLEB8yk2I47-8_5y1_0'

# twitter auth
TWITTER_CONSUMER_KEY = 'sd9StEg1N1qB8gGb2GRX4A'
TWITTER_CONSUMER_SECRET = 'YSKHn8Du6EWqpcWZ6sp5tqDPvcOBXK0WJWVGWyB0'

# facebook auth
FACEBOOK_APP_ID = '211951285561911'
FACEBOOK_API_SECRET = '42efef7e540b80479dbbb69490cd902a'

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
BASE_URL = 'http://unglue.it'
BASE_URL_SECURE = 'https://unglue.it'
IPN_SECURE_URL = False

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
#CKEDITOR_UPLOAD_PATH = '/var/www/static/media/'
#CKEDITOR_UPLOAD_PREFIX = 'https://unglue.it/static/media/'

# decide which of the period tasks to add to the schedule
#CELERYBEAT_SCHEDULE['send_test_email'] = SEND_TEST_EMAIL_JOB
#CELERYBEAT_SCHEDULE['emit_notifications'] = EMIT_NOTIFICATIONS_JOB
# update the statuses of campaigns
CELERYBEAT_SCHEDULE['update_active_campaign_statuses'] = UPDATE_ACTIVE_CAMPAIGN_STATUSES
CELERYBEAT_SCHEDULE['report_new_ebooks'] = EBOOK_NOTIFICATIONS_JOB
CELERYBEAT_SCHEDULE['notify_ending_soon'] = NOTIFY_ENDING_SOON_JOB

# set -- sandbox or production Amazon FPS?
#AMAZON_FPS_HOST = "fps.sandbox.amazonaws.com"
AMAZON_FPS_HOST = "fps.amazonaws.com"

# local settings for maintenance mode
MAINTENANCE_MODE = True

# Amazon keys to permit S3 access
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = 'AKIAIRLBDIET3DFCNU4A'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'unglueit_files'

# if settings/local.py exists, import those settings -- allows for dynamic generation of parameters such as DATABASES
try:
    from regluit.settings.local import *
except ImportError:
    pass
    
# we should suppress Google Analytics outside of production
SHOW_GOOGLE_ANALYTICS = True
