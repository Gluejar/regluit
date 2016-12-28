# coding=utf-8
from .common import *
try:
    from .keys.host import *
except ImportError:
    from .dummy.host import *

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
        'USER': 'regluit',
        'PASSWORD': 'regluit',
        'HOST': '',
        'PORT': '',
        'TEST_CHARSET': 'utf8',
    }
}

TIME_ZONE = 'America/New_York'
SECRET_KEY = u'_^_off!8zsj4+)%qq623m&$7_m-q$iau5le0w!mw&n5tgt#x=t'

# settings for outbout email
# if you have a gmail account you can use your email address and password

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'me@gmail.com'
EMAIL_HOST_PASSWORD = 'my-password'
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'info@gluejar.com'


# formerly of settings/common.py to surface old vars
# TO DO: invalidate before we open source

MAILCHIMP_API_KEY = '5f8e846a2bbc847807ed89086de4b4bf-us2'
MAILCHIMP_NEWS_ID = u'c5cce92fe1'

BOOXTREAM_API_KEY = '7ynRCsx4q21zEY67it7yk8u5rc6EXY'
BOOXTREAM_API_USER = 'ungluetest'

DROPBOX_KEY = '4efhwty5aph52bd'   #for unglue.it, just.unglue.it
#DROPBOX_KEY = '6uefhocpvp0s1ep'  #for localhost

# for reading GITenberg releases
# generated from rdhyee account
GITHUB_PUBLIC_TOKEN = 'f702409f913d7f9046f93c677710f829e2b599c9'

MOBIGEN_URL = "https://docker.gluejar.com:5001/mobigen"
MOBIGEN_USER_ID = "admin"
MOBIGEN_PASSWORD = "CXq5FSEQFgXtP_s"

#-------------------------------------

# twitter auth
SOCIAL_AUTH_TWITTER_KEY = ''
SOCIAL_AUTH_TWITTER_SECRET = ''

# facebook auth
SOCIAL_AUTH_FACEBOOK_KEY = ''
SOCIAL_AUTH_FACEBOOK_SECRET = ''

# get these (as oauth2 client ID and Secret from 
# https://console.developers.google.com/project/569579163337/apiui/credential?authuser=1
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '569579163337-rjija9842834nqa1vi639nac17j1n6cl@developer.gserviceaccount.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'RWPnUkNieUToUtBFaXZjibsU'

# you'll need to register a GoogleBooks API key
# registered to rdhye@gluejar.com on 2013.12.10
GOOGLE_BOOKS_API_KEY = 'AIzaSyC-nBaK90PIsovMRbswPYEKgA6cJfYSDmY'

#BASE_URL = 'http://0.0.0.0/'
BASE_URL_SECURE = 'http://0.0.0.0/'

# Goodreads API
# owned by rdhyee@gluejar.com
GOODREADS_API_KEY = 'w8nsFplG3HFOeOLQ7rqfQ'
GOODREADS_API_SECRET = '8Dfl7nQ28VgzJctlVwf8m7zkPaWns4j79t0G9iFxbk'

# Amazon keys to permit S3 access
# s3_jenkins
# https://console.aws.amazon.com/iam/home?region=us-east-1#/users/s3_jenkins
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = 'AKIAJQGL74HQPHPFYJ5Q'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'jenkins-unglueit'


# use database as queuing service in development
BROKER_TRANSPORT = "djkombu.transport.DatabaseTransport"
INSTALLED_APPS += ("djkombu",)
