from .common import *

ALLOWED_HOSTS = ['.unglue.it']
DEBUG = False
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG
# we are launched!
IS_PREVIEW = False

SITE_ID = 1

ADMINS = (
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
        'TEST': {
            'CHARSET': 'utf8',
        },
        'OPTIONS': {
            'init_command': 'SET max_execution_time=30000'  # In milliseconds; requires MySQL 5.7
        }
    }
}

TIME_ZONE = 'America/New_York'

# settings for outbout email
# if you have a gmail account you can use your email address and password


# Amazon SES

MAIL_USE_TLS = True 
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_PORT = 465
DEFAULT_FROM_EMAIL = 'notices@gluejar.com'

# send celery log to Python logging
WORKER_HIJACK_ROOT_LOGGER = False

# Next step to try https
#BASE_URL = 'http://unglue.it'
BASE_URL_SECURE = 'https://unglue.it'
IPN_SECURE_URL = False

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
#CKEDITOR_UPLOAD_PREFIX = 'https://unglue.it/static/media/'

# start out with nothing scheduled
CELERYBEAT_SCHEDULE = {}

# decide which of the period tasks to add to the schedule
# CELERYBEAT_SCHEDULE['send_test_email'] = SEND_TEST_EMAIL_JOB
# update the statuses of campaigns
CELERYBEAT_SCHEDULE['update_active_campaign_statuses'] = UPDATE_ACTIVE_CAMPAIGN_STATUSES
CELERYBEAT_SCHEDULE['report_new_ebooks'] = EBOOK_NOTIFICATIONS_JOB
CELERYBEAT_SCHEDULE['notify_ending_soon'] = NOTIFY_ENDING_SOON_JOB
CELERYBEAT_SCHEDULE['update_account_statuses'] = UPDATE_ACCOUNT_STATUSES
CELERYBEAT_SCHEDULE['notify_expiring_accounts'] = NOTIFY_EXPIRING_ACCOUNTS
CELERYBEAT_SCHEDULE['refresh_acqs'] = REFRESH_ACQS_JOB
CELERYBEAT_SCHEDULE['refresh_acqs'] = NOTIFY_UNCLAIMED_GIFTS

# set -- sandbox or production Amazon FPS?
#AMAZON_FPS_HOST = "fps.sandbox.amazonaws.com"
AMAZON_FPS_HOST = "fps.amazonaws.com"

# local settings for maintenance mode
MAINTENANCE_MODE = False

# Amazon keys to permit S3 access
# https://console.aws.amazon.com/iam/home?region=us-east-1#/users/s3user?section=security_credentials
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

# we should suppress Google Analytics outside of production
SHOW_GOOGLE_ANALYTICS = True

# if settings/local.py exists, import those settings -- allows for dynamic generation of parameters such as DATABASES
try:
    from regluit.settings.local import *
except ImportError:
    pass
