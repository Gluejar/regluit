# coding=utf-8
from .common import *

ALLOWED_HOSTS = ['.unglue.it']
DEBUG = False
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

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
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': DATABASE_HOST,
        'PORT': '',
        'TEST_CHARSET': 'utf8'
    }
}

TIME_ZONE = 'America/New_York'

# settings for outbout email
# if you have a gmail account you can use your email address and password

# Amazon SES

EMAIL_BACKEND = 'django_smtp_ssl.SSLEmailBackend'
MAIL_USE_TLS = True 
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_PORT = 465
DEFAULT_FROM_EMAIL = 'notices@gluejar.com'

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
MAINTENANCE_MODE = False

# if settings/local.py exists, import those settings -- allows for dynamic generation of parameters such as DATABASES
try:
    from regluit.settings.local import *
except ImportError:
    pass
