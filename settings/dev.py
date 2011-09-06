from regluit.settings.common import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'regluit.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

TIME_ZONE = 'America/New_York'
SECRET_KEY = '_^_off!8zsj4+)%qq623m&$7_m-q$iau5le0w!mw&n5tgt#x=t'

# settings for outbout email
# if you have a gmail account you can use your email address and password

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'me@gmail.com'
EMAIL_HOST_PASSWORD = 'my-password'
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'info@gluejar.com'

# twitter auth
# you'll need to create a new Twitter application to fill in these blanks
# https://dev.twitter.com/apps/new

TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''

# facebook auth
# you'll need to create a new Facebook application to fill in these blanks
# https://developers.facebook.com/apps/

FACEBOOK_APP_ID = ''
FACEBOOK_API_SECRET = ''

# google auth
# you'll need to create a new Google application to fill in these blanks
# https://code.google.com/apis/console/
GOOGLE_OAUTH2_CLIENT_ID = '989608723367.apps.googleusercontent.com'
GOOGLE_OAUTH2_CLIENT_SECRET = '3UqalKyNynnaaarumUIWh8vS'
GOOGLE_DISPLAY_NAME = 'unglue it!'

