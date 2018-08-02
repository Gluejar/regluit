import datetime
import mimetypes
import sys
import os
from os.path import dirname, realpath, join

import regluit
from regluit.payment.parameters import PAYMENT_HOST_PAYPAL, PAYMENT_HOST_AMAZON

from regluit.utils import custom_logging
import logging.handlers
logging.handlers.GroupWriteRotatingFileHandler = custom_logging.GroupWriteRotatingFileHandler

PROJECT_DIR = dirname(dirname(realpath(__file__)))

LANGUAGE_CODE = 'en-us'
LANGUAGES = (
    ('en', 'English'),
)
LOCAL_TEST = False
TESTING = sys.argv[1:2] == ['test'] # detect if we're running tests (used to turn off a repair migration)
ALLOWED_HOSTS = ['.unglue.it', '.unglueit.com',]

WISHED_LANGS = ('en','fr','es','de','el','pt','it','ru','cs','ja','zh','nl','ut','ar','la','id','ca','fa','sv','sl','ko','tr')

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# set once instead of in all the templates
JQUERY_HOME = "/static/js/jquery-1.12.4.min.js"
JQUERY_UI_HOME = "/static/js/jquery-ui-1.11.4.min.js"
JQUERY_UI_THEME = "/static/css/ui-lightness/jquery-ui-1.11.4.min.css"

CKEDITOR_UPLOAD_PATH = ''
CKEDITOR_RESTRICT_BY_USER = True
CKEDITOR_CONFIGS = {
    'default': {
        'width': 700,
        'toolbar': [
            ['Cut','Copy','Paste', 'PasteFromWord', '-', 'Undo', 'Redo', '-', 'Source'],
            ['Bold', 'Italic', 'RemoveFormat', '-', 'NumberedList','BulletedList', '-','Blockquote'],
            ['Find','Replace','-', 'Scayt'],
            ['Link', 'Unlink', '-', 'Image','HorizontalRule']
         ],
         'disallowedContent': '*[style]{font*} script style *[on*]{*}',
    },
}
CKEDITOR_JQUERY_URL=JQUERY_HOME

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

SASS_PROCESSOR_ROOT = os.path.join(PROJECT_DIR, 'static')

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
# ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    join(PROJECT_DIR, 'static'),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = u'a+bo0@3$n18e(newe7og6hmq$r#bkib73z(+s*n25%6q3+22jo'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [join(PROJECT_DIR, "frontend", "templates"),
                 join(PROJECT_DIR, "frontend", "templates", "registration"),
                 join(PROJECT_DIR, "frontend", "questionnaire"),
                 ],
        'OPTIONS':{
            'context_processors':[
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'regluit.context_processors.is_preview',
                'regluit.context_processors.count_unseen',
                ],
            'loaders':[
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                ],

        }
    },
]


MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'regluit.libraryauth.auth.SocialAuthExceptionMiddlewareWithoutMessages',
    'django.middleware.locale.LocaleMiddleware',
    'questionnaire.request_cache.RequestCacheMiddleware',
)

ROOT_URLCONF = 'regluit.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',  
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_comments',
    'django.contrib.humanize',
    'django_extensions',
    'regluit.frontend',
    'regluit.api',
    'regluit.bisac',
    'regluit.core',
    'regluit.marc',
    'regluit.payment',
    'regluit.utils',
    'registration',
    'social_django',
    'tastypie',
    'djcelery',
    'el_pagination',
    'selectable',
    'regluit.frontend.templatetags',
    'notification',
    'email_change',
    'ckeditor',
    'ckeditor_uploader',
    'storages', 
    'sorl.thumbnail',
    'mptt',   
    # this must appear *after* django.frontend or else it overrides the 
    # registration templates in frontend/templates/registration
    'django.contrib.admin',
    'regluit.distro',               
    'regluit.booxtream',
    'regluit.pyepub',
    'regluit.libraryauth', 
    'transmeta',
    'questionnaire',
    'questionnaire.page',  
    'sass_processor',
)

SASS_PROCESSOR_INCLUDE_DIRS = [
    os.path.join(PROJECT_DIR, 'static', 'scss'),
]
SASS_PROCESSOR_AUTO_INCLUDE = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'brief': {
            'format': '%(asctime)s %(levelname)s %(name)s[%(funcName)s]: %(message)s',
        },
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(server_time)s] %(message)s',
        },
    },
    'filters': {
         'require_debug_false': {
             '()': 'django.utils.log.RequireDebugFalse'
         }
     },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.GroupWriteRotatingFileHandler',
            'filename': join(PROJECT_DIR, 'logs', 'unglue.it.log'),
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter': 'brief',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
        '': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    }
}

# django-registration
EMAIL_HOST = 'smtp.gluejar.com'
DEFAULT_FROM_EMAIL = 'notices@gluejar.com'
SERVER_EMAIL = 'notices@gluejar.com'
SUPPORT_EMAIL = 'unglueit@ebookfoundation.org'
ACCOUNT_ACTIVATION_DAYS = 30
SESSION_COOKIE_AGE = 3628800 # 6 weeks

# django-socialauth
AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.yahoo.YahooOpenId',
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.open_id.OpenIdAuth',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_ENABLED_BACKENDS = ['google', 'facebook', 'twitter']
#SOCIAL_AUTH_ASSOCIATE_BY_MAIL = True
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/'
SOCIAL_AUTH_SLUGIFY_USERNAMES = True
SOCIAL_AUTH_NONCE_SERVER_URL_LENGTH = 200
SOCIAL_AUTH_ASSOCIATION_SERVER_URL_LENGTH = 135
SOCIAL_AUTH_ASSOCIATION_HANDLE_LENGTH = 125
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {'fields': 'picture'}
SOCIAL_AUTH_FACEBOOK_LOGIN_ERROR_URL = '/'
SOCIAL_AUTH_TWITTER_LOGIN_ERROR_URL = '/'

SOCIAL_AUTH_PIPELINE = (
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. On some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    'social_core.pipeline.social_auth.social_details',

    # Get the social uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    'social_core.pipeline.social_auth.social_uid',

    # Verifies that the current auth process is valid within the current
    # project, this is were emails and domains whitelists are applied (if
    # defined).
    'social_core.pipeline.social_auth.auth_allowed',

    # Checks if the current social-account is already associated in the site.
    'regluit.libraryauth.auth.selective_social_user',

    # Make up a username for this person, appends a random string at the end if
    # there's any collision.
    'social_core.pipeline.user.get_username',
    
    # make username < 222 in length
    'regluit.libraryauth.auth.chop_username',
    
    # Send a validation email to the user to verify its email address.
    # Disabled by default.
    # 'social_core.pipeline.mail.mail_validation',
    
    # Associates the current social details with another user account with
    # a similar email address. don't use twitter or facebook to log in
    'regluit.libraryauth.auth.selectively_associate_by_email',

    # Create a user account if we haven't found one yet.
    'social_core.pipeline.user.create_user',

    # Create the record that associated the social account with this user.
    'social_core.pipeline.social_auth.associate_user',
    
    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    'social_core.pipeline.social_auth.load_extra_data',

    # add extra data to user profile
    'regluit.libraryauth.auth.deliver_extra_data',

    # Update the user record with any changed info from the auth service.
    'social_core.pipeline.user.user_details'
)

SOCIAL_AUTH_TWITTER_EXTRA_DATA = [('profile_image_url_https', 'profile_image_url_https'),('screen_name','screen_name')]

LOGIN_URL = "/accounts/superlogin/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_URL = "/accounts/logout/"
LOGIN_ERROR_URL    = '/accounts/login-error/'

USER_AGENT = "unglue.it.bot v0.0.1 <https://unglue.it>"

# The amount of the transaction that Gluejar takes 
GLUEJAR_COMMISSION = 0.06
PREAPPROVAL_PERIOD = 365 # days to ask for in a preapproval
PREAPPROVAL_PERIOD_AFTER_CAMPAIGN = 90 # if we ask for preapproval time after a campaign deadline
PAYPAL_GLUEJAR_EMAIL = 'info@ebookfoundation.org' #legacy code needs this

# How many days we will try to collect on failed transactions until they are written off
RECHARGE_WINDOW = 14

GOODREADS_API_KEY = ""
GOODREADS_API_SECRET = ""

# unglue.it parameters
UNGLUEIT_MINIMUM_TARGET = 500 # in US Dollars
UNGLUEIT_MAXIMUM_TARGET = 10000000 # in US Dollars
UNGLUEIT_LONGEST_DEADLINE = '180' # number of days allowed for a campaign
UNGLUEIT_RECOMMENDED_USERNAME = 'unglueit'
B2U_TERM = datetime.timedelta(days=5*365 +1 ) # 5 years?
MAX_CC_DATE = datetime.date( 2099,12,31)

TEST_RUNNER = "djcelery.contrib.test_runner.CeleryTestSuiteRunner"
import djcelery
djcelery.setup_loader()

# Mailchimp archive JavaScript URL
CAMPAIGN_ARCHIVE_JS = "http://us2.campaign-archive1.com/generate-js/?u=15472878790f9faa11317e085&fid=28161&show=10"

# periodic tasks for celery
# start out with nothing scheduled
CELERYBEAT_SCHEDULE = {}
from celery.schedules import crontab
# define some periodic tasks

SEND_TEST_EMAIL_JOB = {
    "task": "regluit.core.tasks.send_mail_task",
    "schedule": crontab(hour=18, minute=20),
    "args": ('hi there  18:20', 'testing 1, 2, 3', 'notices@gluejar.com', ['raymond.yee@gmail.com'])
}

UPDATE_ACTIVE_CAMPAIGN_STATUSES = {
    "task": "regluit.core.tasks.update_active_campaign_status",
    "schedule": crontab(hour=0, minute=1),
    "args": ()
}

EBOOK_NOTIFICATIONS_JOB = {
    "task": "regluit.core.tasks.report_new_ebooks",
    "schedule": crontab(hour=0, minute=30),
    "args": ()    
}

NOTIFY_ENDING_SOON_JOB = {
    "task": "regluit.core.tasks.notify_ending_soon",
    "schedule": crontab(hour=1, minute=0),
    "args": ()
}

REFRESH_ACQS_JOB = {
    "task": "regluit.core.tasks.refresh_acqs",
    "schedule": datetime.timedelta(minutes=10),
    "args": ()
}

UPDATE_ACCOUNT_STATUSES = {
    "task": "regluit.payment.tasks.update_account_status",
    "schedule": crontab(day_of_month=1, hour=0, minute=0),
    "args": ()
}

NOTIFY_EXPIRING_ACCOUNTS = {
    "task": "regluit.payment.tasks.notify_expiring_accounts",
    "schedule": crontab(day_of_month=22, hour=0, minute=30),
    "args": ()    
}

NOTIFY_UNCLAIMED_GIFTS = {
    "task": "regluit.core.tasks.notify_unclaimed_gifts",
    "schedule": crontab( hour=2, minute=15),
    "args": ()    
}

# by default, in common, we don't turn any of the celerybeat jobs on -- turn them on in the local settings file

# set notification queueing on
NOTIFICATION_QUEUE_ALL = True
# amazon or paypal for now.
PAYMENT_PROCESSOR = 'stripelib'


# we should suppress Google Analytics outside of production
SHOW_GOOGLE_ANALYTICS = False

# to enable uploading to S3 and integration of django-storages + django-ckeditor
# some variables to be overriddden in more specific settings files -- e.g., prod.py, 
CKEDITOR_ALLOW_NONIMAGE_FILES = False

AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
AWS_STORAGE_BUCKET_NAME = ''
AWS_QUERYSTRING_AUTH = False


FORMATS = (
    ('pdf','PDF'),
    ('epub','EPUB'),
    ('html','HTML'),
    ('text','TEXT'),
    ('mobi','MOBI'),
)

# used by MARC. maybe should use python's mimetypes
CONTENT_TYPES = {
    'pdf': 'application/pdf',
    'epub': 'application/epub+zip',
    'html': 'text/html',
    'text': 'text/plain',
    'mobi': 'application/x-mobipocket-ebook'
}

mimetypes.init(["{}/deploy/mime.types".format(PROJECT_DIR)])

# if you add more of these, make sure core/marc.py can deal
MARC_CHOICES = (
    ('DIRECT', 'Raw link'),
    ('UNGLUE', 'Unglue.it link'),
    ('B2U', 'Library link'),
)
MARC_PREF_OPTIONS =(
    ('DIRECT', 'Raw link'),
    ('UNGLUE', 'Unglue.it link'),
)


BOOXTREAM_TEST_EPUB_URL = 'https://github.com/Gluejar/open_access_ebooks_ebook/raw/master/download/open_access_ebooks.epub'
TEST_PDF_URL = "https://github.com/Gluejar/flatland/raw/master/downloads/Flatland.pdf"
FILE_UPLOAD_MAX_MEMORY_SIZE = 20971520 #20MB

QUESTIONNAIRE_USE_SESSION = False
QUESTIONNAIRE_DEBUG = True
QUESTIONNAIRE_ITEM_MODEL = 'core.Work'
QUESTIONNAIRE_SHOW_ITEM_RESULTS = False

# Selenium related -- set if Se tests run
FIREFOX_PATH = ''
CHROMEDRIVER_PATH = ''

try:
    from .keys.common import *
except ImportError:
    print 'no real key file found, using dummy'
    from .dummy.common import *

try:
    from .keys.host import *
    TEST_INTEGRATION = True
except ImportError:
    from .dummy.host import *
    TEST_INTEGRATION = False
    LOCAL_TEST = True

if AWS_SECRET_ACCESS_KEY:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
else:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage' 

