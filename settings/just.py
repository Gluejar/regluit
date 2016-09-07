from regluit.settings.common import *

ALLOWED_HOSTS = ['.unglue.it']
DEBUG = False
TEMPLATES[0]['OPTIONS']['debug'] = DEBUGG

SITE_ID = 5

ADMINS = (
    ('Raymond Yee', 'rdhyee+ungluebugs@gluejar.com'),
    ('Eric Hellman', 'eric@gluejar.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'unglueit',
        'USER': 'root',
        'PASSWORD': 'forgetn0t',
        'HOST': 'justdb1.cboagmr25pjs.us-east-1.rds.amazonaws.com',
        'PORT': '',
        'TEST_CHARSET': 'utf8'
    }
}

TIME_ZONE = 'America/New_York'
SECRET_KEY = u'_^_off!8zsj4+)%qq623m&$7_m-q$iau5le0w!mw&n5tgt#x=t'

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
# key created by rdhyee@gluejar.com 2013/07/02
GOOGLE_BOOKS_API_KEY = 'AIzaSyBPZS7D3QvypGN_Tqc3blAXV1iJJJuu4mk'

# twitter auth
SOCIAL_AUTH_TWITTER_KEY = 'sd9StEg1N1qB8gGb2GRX4A'
SOCIAL_AUTH_TWITTER_SECRET = 'YSKHn8Du6EWqpcWZ6sp5tqDPvcOBXK0WJWVGWyB0'

# facebook auth (for just)
# created by Raymond Yee
# https://developers.facebook.com/apps/236518556394209/settings/
SOCIAL_AUTH_FACEBOOK_KEY = '236518556394209'
SOCIAL_AUTH_FACEBOOK_SECRET = '88fec4d1dfc1ef4438cb87efa171db28'

# get these (as oauth2 client ID and Secret from 
# https://console.developers.google.com/project/569579163337/apiui/credential?authuser=1
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '569579163337-kq3vm5imdap4hapj1r8lvmcg05kfi6ii.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'IYmgelotf77H8OPWX8oXf4Cq'

# Goodreads API
GOODREADS_API_KEY = "vfqIO6QAhBVvlxt6hAzZJg"
GOODREADS_API_SECRET = "57tq4MpyJ15Hgm2ToZQQFWJ7vraZzOAqHLckWRXQ"

# Freebase credentials
FREEBASE_USERNAME = ''
FREEBASE_PASSWORD = ''

# send celery log to Python logging
CELERYD_HIJACK_ROOT_LOGGER = False

# Next step to try https
#BASE_URL = 'http://just.unglue.it'
BASE_URL_SECURE = 'https://just.unglue.it'
IPN_SECURE_URL = False

# use redis for production queue
BROKER_TRANSPORT = "redis"
BROKER_HOST = "localhost"
BROKER_PORT = 6379
BROKER_VHOST = "0"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'brief': {
            'format': '%(asctime)s %(levelname)s %(name)s[%(funcName)s]: %(message)s',
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': join('/var/log/regluit', 'unglue.it.log'),
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter': 'brief',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
        '': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
    }
}

STATIC_ROOT = '/var/www/static'
#CKEDITOR_UPLOAD_PATH = '/var/www/static/media/'
#CKEDITOR_UPLOAD_PREFIX = 'https://just.unglue.it/static/media/'

IS_PREVIEW = False

# decide which of the period tasks to add to the schedule
CELERYBEAT_SCHEDULE['send_test_email'] = SEND_TEST_EMAIL_JOB
CELERYBEAT_SCHEDULE['report_new_ebooks'] = EBOOK_NOTIFICATIONS_JOB


CELERYBEAT_SCHEDULE['update_account_statuses'] = UPDATE_ACCOUNT_STATUSES
CELERYBEAT_SCHEDULE['notify_expiring_accounts'] = NOTIFY_EXPIRING_ACCOUNTS
CELERYBEAT_SCHEDULE['refresh_acqs'] = REFRESH_ACQS_JOB


# set -- sandbox or production Amazon FPS?
AMAZON_FPS_HOST = "fps.sandbox.amazonaws.com"
#AMAZON_FPS_HOST = "fps.amazonaws.com"

# local settings for maintenance mode
MAINTENANCE_MODE = True

# Amazon keys to permit S3 access

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = 'AKIAIYP6XRVAUWKQFT5Q'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'just-unglueit'

# if settings/local.py exists, import those settings -- allows for dynamic generation of parameters such as DATABASES
try:
    from regluit.settings.local import *
except ImportError:
    pass
