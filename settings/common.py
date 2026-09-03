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

# Django 3.2+: preserve existing auto-field behavior for legacy models
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Mask secrets the default filter misses (STRIPE_SK, EMAIL_HOST_USER, ...) in the
# settings dump emailed on every 500. See EbookFoundation/security-private#22.
DEFAULT_EXCEPTION_REPORTER_FILTER = 'regluit.utils.exception_filter.RegluitSafeExceptionReporterFilter'

# Django 4.x defaults to JSONSerializer; make this explicit so existing sessions
# aren't broken during the upgrade. Flush sessions during production cutover.
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

LANGUAGE_CODE = 'en-us'
LANGUAGES = (
    ('en', 'English'),
)
LOCAL_TEST = False
TEST_PLATFORM = 'production'
TESTING = sys.argv[1:2] == ['test'] # detect if we're running tests (used to turn off a repair migration)
ALLOWED_HOSTS = ['.unglue.it', '.unglueit.com',]

WISHED_LANGS = ('en','fr','es','de','el','pt','it','ru','cs','ja','zh','nl','ut','ar','la','id','ca','fa','sv','sl','ko','tr')

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# USE_L10N was removed in Django 5.0 (localized formatting is always on), so it
# is intentionally not set here.

# Django 5.0 flipped the USE_TZ default from False to True. This codebase (and
# the production database contents) use naive local datetimes throughout, so we
# pin the pre-5.0 behavior. Migrating to timezone-aware datetimes is a separate
# project (data migration + audit of every datetime comparison), not part of the
# 4.2 -> 5.2 upgrade.
USE_TZ = False

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
    'django.contrib.humanize',
    'django_extensions',
    'regluit.frontend',
    'regluit.api',
    'regluit.bisac',
    'regluit.core',
    'regluit.marc',
    'regluit.payment',
    'regluit.utils',
    'django_registration',
    'social_django',
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
    'pyepub',
    'regluit.libraryauth', 
    'questionnaire',
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
        'dl': {
            'format': '%(asctime)s : %(message)s',
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
        'downloads': {
            'level': 'INFO',
            'class': 'logging.handlers.GroupWriteRotatingFileHandler',
            'filename': join(PROJECT_DIR, 'logs', 'downloads.log'),
            'maxBytes': 1024*1024*10, # 10 MB
            'backupCount': 8,
            'formatter': 'dl',
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
        'regluit.downloads': {
            'handlers': ['downloads'],
            'propagate': False,
        },
        # Without an explicit entry here, LOGGING's disable_existing_loggers
        # (True, above) disables this logger outright the moment
        # settings/common.py imports regluit.utils.safe_email_backend --
        # verified live (Codex review round 2, 2026-08-31): its ERROR calls
        # (the ones meant to make a Celery-swallowed send refusal visible;
        # see EMAIL_SAFE_MODE below) silently did nothing without this.
        'regluit.utils.safe_email_backend': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
        '': {
            'handlers': ['file'],
            'level': 'INFO',
        },
# uncomment to do SQL logging
#       'django.db.backends': {
#           'level': 'DEBUG',
#           'handlers': ['file'],
#        },
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'regluit',
    }
}

# django-registration
EMAIL_HOST = 'smtp.gluejar.com'
DEFAULT_FROM_EMAIL = 'notices@gluejar.com'
SERVER_EMAIL = 'notices@gluejar.com'
SUPPORT_EMAIL = 'unglueit@ebookfoundation.org'
ACCOUNT_ACTIVATION_DAYS = 30
SESSION_COOKIE_AGE = 604800 # 7 days

# django-socialauth
# Google OAuth2 login removed 2026-08-30 (Eric: "lets remove the log in with
# google button" -- Gmail thread 1a04cd3f47fac2a2, in response to Google's
# unused-OAuth-client notice; client 569579163337-... left inactive to expire
# ~Sept 25, 2026). social_django / OpenIdAuth stay installed: OpenIdAuth is
# still a registered (if unused) backend, and existing Google-linked users'
# UserSocialAuth rows must remain queryable, so the app/pipeline/URLs are
# untouched -- only the Google-specific backend + its templates/settings go.
AUTHENTICATION_BACKENDS = (
    'social_core.backends.open_id.OpenIdAuth',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/'
SOCIAL_AUTH_SLUGIFY_USERNAMES = True
SOCIAL_AUTH_NONCE_SERVER_URL_LENGTH = 200
SOCIAL_AUTH_ASSOCIATION_SERVER_URL_LENGTH = 135
SOCIAL_AUTH_ASSOCIATION_HANDLE_LENGTH = 125

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
    # a similar email address.
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
LOGOUT_REDIRECT_URL = "/"
LOGOUT_URL = "/accounts/logout/"
LOGIN_ERROR_URL    = '/accounts/login-error/'

USER_AGENT = "unglue.it.bot v0.0.1 (https://unglue.it)"

# The amount of the transaction that Gluejar takes 
GLUEJAR_COMMISSION = 0.06
PREAPPROVAL_PERIOD = 365 # days to ask for in a preapproval
PREAPPROVAL_PERIOD_AFTER_CAMPAIGN = 90 # if we ask for preapproval time after a campaign deadline
PAYPAL_GLUEJAR_EMAIL = 'info@ebookfoundation.org' #legacy code needs this

# How many days we will try to collect on failed transactions until they are written off
RECHARGE_WINDOW = 14

# unglue.it parameters
UNGLUEIT_MINIMUM_TARGET = 500 # in US Dollars
UNGLUEIT_MAXIMUM_TARGET = 10000000 # in US Dollars
UNGLUEIT_LONGEST_DEADLINE = '180' # number of days allowed for a campaign
UNGLUEIT_RECOMMENDED_USERNAME = 'unglueit'
B2U_TERM = datetime.timedelta(days=5*365 +1 ) # 5 years?
MAX_CC_DATE = datetime.date( 2099,12,31)

# Mailchimp archive JavaScript URL
CAMPAIGN_ARCHIVE_JS = "http://us2.campaign-archive1.com/generate-js/?u=15472878790f9faa11317e085&fid=28161&show=10"

# use redis for production queue and results
CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/1"
CELERY_LOG_DIR = ""

# periodic tasks for celery
from celery.schedules import crontab
# define some periodic tasks

UPDATE_ACTIVE_CAMPAIGN_STATUSES = {
    "task": "regluit.core.tasks.update_active_campaign_status",
    "schedule": crontab(day_of_month='*', hour=0, minute=1),
    "args": ()
}

EBOOK_NOTIFICATIONS_JOB = {
    "task": "regluit.core.tasks.report_new_ebooks",
    "schedule": crontab(day_of_month='*', hour=0, minute=30),
    "args": ()    
}

NOTIFY_ENDING_SOON_JOB = {
    "task": "regluit.core.tasks.notify_ending_soon",
    "schedule": crontab(day_of_month='*', hour=1, minute=0),
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
    "schedule": crontab(day_of_month='*', hour=2, minute=15),
    "args": ()    
}

SAVE_INFO_PAGE = {
    "task": "regluit.frontend.tasks.save_info_page",
    "schedule": crontab(day_of_month='*', hour=0, minute=40),
    "args": ()    
}

PERIODIC_CLEANUP = {
    "task": "regluit.core.tasks.periodic_cleanup",
    "schedule": crontab(hour=0, minute=35),
    "args": ()    
}

EMIT_NOTICES = {
    "task": "regluit.core.tasks.emit_notifications",
    "schedule": crontab(minute='1,11,21,31,41,51'),
    "args": ()    
}

FEATURE_NEW_WORK = {
    "task": "regluit.core.tasks.feature_new_work",
    "schedule": crontab(day_of_week=1, hour=9, minute=30),
    "args": ()    
}

# by default, in common, we don't turn any of the celerybeat jobs on -- turn them on in the local settings file

# set notification queueing on
NOTIFICATION_QUEUE_ALL = True
# amazon or paypal for now.
PAYMENT_PROCESSOR = 'stripelib'

# allow application code to catch thumbnailing errors
THUMBNAIL_DEBUG = True
THUMBNAIL_FORCE_OVERWRITE = False
THUMBNAIL_REMOVE_URL_ARGS = False
THUMBNAIL_URL_TIMEOUT = 60
# use redis
# THUMBNAIL_KVSTORE = 'sorl.thumbnail.kvstores.redis_kvstore.KVStore'

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

USE_OPENLIBRARY = False

# Selenium related -- set if Se tests run
FIREFOX_PATH = ''
CHROMEDRIVER_PATH = ''
GOOGLEBOT_UA = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
CHROME_UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15'


try:
    from .keys.common import *
except ImportError:
    print('no real key file found, using dummy')
    from .dummy.common import *

try:
    from .keys.host import *
    TEST_INTEGRATION = True
except ImportError:
    from .dummy.host import *
    TEST_INTEGRATION = False
    LOCAL_TEST = True

# DEFAULT_FILE_STORAGE / STATICFILES_STORAGE were removed in Django 5.1 in favor of
# the STORAGES dict. STORAGES is available since Django 4.2, so this is forward-
# compatible and behaves identically on the current 4.2 runtime.
if AWS_SECRET_ACCESS_KEY:
    _default_file_backend = 'storages.backends.s3boto3.S3Boto3Storage'
else:
    _default_file_backend = 'django.core.files.storage.FileSystemStorage'

STORAGES = {
    'default': {'BACKEND': _default_file_backend},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}

# we wond't record downloads for an ebook if their more than this in a month
DOWNLOAD_LOGS_MAX = 499

# Non-production email safety net (regluit#1238). A staging/test box whose
# database has been refreshed from a copy of production holds real users'
# real email addresses -- without this, its normal mail-sending code
# (password resets, gift notices, campaign emails, ...) would deliver to
# those real people. Off by default (empty string) so production, and any
# environment that hasn't explicitly opted in, are unaffected.
#
# IMPORTANT if you're touching settings after this point: this must be the
# LAST thing in the settings chain to set EMAIL_BACKEND. Any settings module
# that does `from .common import *` and then re-sets EMAIL_BACKEND itself
# (settings/spike.py already does exactly this, for an unrelated reason)
# silently defeats this safety net. Verified 2026-08-31 that the actual
# deploy template (regluit-provisioning/roles/regluit_prod/templates/
# prod.py.j2, which is what test.unglue.it/unglue.it actually run as
# regluit.settings.prod) does NOT re-set EMAIL_BACKEND after `from .common
# import *` -- but that's an external file this repo doesn't control, so it
# stays a live risk for any future change there. (CC review, 2026-08-31.)
from regluit.utils.safe_email_backend import resolve_email_backend  # noqa: E402

EMAIL_SAFE_MODE = os.environ.get('EMAIL_SAFE_MODE', '').strip().lower() in ('1', 'true', 'yes')
SAFE_EMAIL_REAL_BACKEND, EMAIL_BACKEND = resolve_email_backend(
    EMAIL_SAFE_MODE,
    globals().get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend'),
)
if EMAIL_SAFE_MODE:
    EMAIL_SAFE_MODE_ALLOWED_DOMAINS = os.environ.get('EMAIL_SAFE_MODE_ALLOWED_DOMAINS', '')
    EMAIL_SAFE_MODE_ALLOWED_ADDRESSES = os.environ.get('EMAIL_SAFE_MODE_ALLOWED_ADDRESSES', '')
    EMAIL_SAFE_MODE_REDIRECT_TO = os.environ.get('EMAIL_SAFE_MODE_REDIRECT_TO', '')