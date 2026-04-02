# coding=utf-8
# Docker development settings
from .common import *
from .dummy.host import *

DEBUG = True
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

IS_PREVIEW = False
SITE_ID = 3

ALLOWED_HOSTS = ['*']

ADMINS = (
    ('Docker Dev', 'dev@localhost'),
)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'unglueit',
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': DATABASE_HOST,
        'PORT': '3306',
        'TEST': {
            'CHARSET': 'utf8',
        },
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

TIME_ZONE = 'America/New_York'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

REDIRECT_IS_HTTPS = False
BASE_URL_SECURE = 'http://localhost:8000'

# Celery uses Redis in Docker
BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/1'

WORKER_HIJACK_ROOT_LOGGER = False

STATIC_ROOT = '/var/www/static'

CELERYBEAT_SCHEDULE = {}

MAINTENANCE_MODE = False

# Cloudflare Turnstile (disabled for local dev)
CF_TURNSTILE_SITE_KEY = ''
CF_TURNSTILE_SECRET_KEY = ''

# Dummy Mailchimp key that passes format validation without looking like a real secret
MAILCHIMP_API_KEY = ('0' * 32) + '-us2'
MAILCHIMP_NEWS_ID = '0000000000'

SASS_OUTPUT_STYLE = 'compressed'

# Disable SASS compilation for Docker dev (use pre-compiled CSS)
SASS_PROCESSOR_ENABLED = False

# Log to console in Docker
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
