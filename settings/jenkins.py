from regluit.settings.common import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
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
IPN_SECURE_URL = False

# Goodreads API
GOODREADS_API_KEY = 'w8nsFplG3HFOeOLQ7rqfQ'
GOODREADS_API_SECRET = '8Dfl7nQ28VgzJctlVwf8m7zkPaWns4j79t0G9iFxbk'

# Amazon keys to permit S3 access
# s3_jenkins
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = 'AKIAJQGL74HQPHPFYJ5Q'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'jenkins-unglueit'


# use database as queuing service in development
BROKER_TRANSPORT = "djkombu.transport.DatabaseTransport"
INSTALLED_APPS += ("djkombu",)
