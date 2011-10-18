from regluit.settings.common import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Ed Summers', 'ehs@pobox.com'),
    ('Raymond Yee', 'rdhyee+ungluebugs@gluejar.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'unglueit_dev',
        'USER': 'unglueit_dev',
        'PASSWORD': 'unglu3it',
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
