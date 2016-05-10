from regluit.settings.common import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

SITE_ID = 2

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
SOCIAL_AUTH_TWITTER_KEY = 'sd9StEg1N1qB8gGb2GRX4A'
SOCIAL_AUTH_TWITTER_SECRET = 'YSKHn8Du6EWqpcWZ6sp5tqDPvcOBXK0WJWVGWyB0'

# facebook auth (for localvm)
# https://developers.facebook.com/apps/401501793375379/settings/
SOCIAL_AUTH_FACEBOOK_KEY = '401501793375379'
SOCIAL_AUTH_FACEBOOK_SECRET = '7b63412aa28f408e6349eb0eceb1fcc3'

# get these (as oauth2 client ID and Secret from 
# https://console.developers.google.com/project/grand-analyzer-95823/apiui/credential?clientType&authuser=0#
# rdhyee@gluejar.com account

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '559408900801-vrucvpqr73i1svmo5g8lu9e0apuv2i43.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'pTErzrpTrn55Yj39APWlMd-L'

# Goodreads API
GOODREADS_API_KEY = "vfqIO6QAhBVvlxt6hAzZJg"
GOODREADS_API_SECRET = "57tq4MpyJ15Hgm2ToZQQFWJ7vraZzOAqHLckWRXQ"

# Freebase credentials
FREEBASE_USERNAME = ''
FREEBASE_PASSWORD = ''

# send celery log to Python logging
CELERYD_HIJACK_ROOT_LOGGER = False

# Next step to try https
#BASE_URL = 'http://127.0.0.1'
BASE_URL_SECURE = 'https://127.0.0.1:443'
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
CKEDITOR_UPLOAD_PATH = '/var/www/static/media/'

IS_PREVIEW = False

# decide which of the period tasks to add to the schedule
#CELERYBEAT_SCHEDULE['send_test_email'] = SEND_TEST_EMAIL_JOB
CELERYBEAT_SCHEDULE['report_new_ebooks'] = EBOOK_NOTIFICATIONS_JOB



# local settings for maintenance mode
MAINTENANCE_MODE = False

# Amazon keys to permit S3 access
# reusing just cedentials here

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = 'AKIAIYP6XRVAUWKQFT5Q'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'just-unglueit'



# if settings/local.py exists, import those settings -- allows for dynamic generation of parameters such as DATABASES
try:
    from regluit.settings.local import *
except ImportError:
    pass
