# coding=utf-8
from .common import *

DEBUG = True
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG
IS_PREVIEW = False

ADMINS = (
    ('Raymond Yee', 'rdhyee+ungluebugs@gluejar.com'),
    ('Eric Hellman', 'eric@gluejar.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'regluit',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'TEST': {
            'CHARSET': 'utf8',
        }
    }
}

TIME_ZONE = 'America/New_York'

# settings for outbout email
# if you have a gmail account you can use your email address and password

EMAIL_BACKEND = 'django_smtp_ssl.SSLEmailBackend'
MAIL_USE_TLS = True 
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_PORT = 465
DEFAULT_FROM_EMAIL = 'notices@gluejar.com'


# formerly of settings/common.py to surface old vars
# TO DO: invalidate before we open source

# for use with test google account only
GOOGLE_DISPLAY_NAME = 'Unglue.It'
REDIRECT_IS_HTTPS = False

#BASE_URL = 'http://0.0.0.0/'
BASE_URL_SECURE = 'http://0.0.0.0/'

BROKER_TRANSPORT = "redis"
BROKER_HOST = "localhost"
BROKER_PORT = 6379
BROKER_VHOST = "0"

# Amazon  S3 access
AWS_STORAGE_BUCKET_NAME = 'unglueit-testfiles'

SOCIAL_AUTH_TWITTER_KEY = ''
SOCIAL_AUTH_TWITTER_SECRET = ''
SOCIAL_AUTH_FACEBOOK_KEY = ''
SOCIAL_AUTH_FACEBOOK_SECRET = ''
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = ''
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ''
GOOGLE_BOOKS_API_KEY = ''
TEST_INTEGRATION = False
LOCAL_TEST = True
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

