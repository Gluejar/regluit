from os.path import dirname, realpath, join
import regluit
import datetime
from regluit.payment.parameters import PAYMENT_HOST_PAYPAL, PAYMENT_HOST_AMAZON

PROJECT_DIR = dirname(dirname(realpath(__file__)))

LANGUAGE_CODE = 'en-us'

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
MEDIA_URL = ''

CKEDITOR_UPLOAD_PATH = ''
CKEDITOR_RESTRICT_BY_USER = True
CKEDITOR_CONFIGS = {
    'default': {
        'width': 700,
        'toolbar': [
            ['Cut','Copy','Paste', 'PasteFromWord', '-', 'Undo', 'Redo', '-', 'Source'],
            ['Bold', 'Italic', '-', 'NumberedList','BulletedList', '-','Blockquote'],
            ['Find','Replace','-', 'Scayt'],
            ['Link', 'Unlink', '-', 'Image', 'HorizontalRule']
         ],
    },
}

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

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
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'a+bo0@3$n18e(newe7og6hmq$r#bkib73z(+s*n25%6q3+22jo'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    'regluit.context_processors.is_preview',
    'regluit.context_processors.count_unseen',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'maintenancemode.middleware.MaintenanceModeMiddleware',
)

ROOT_URLCONF = 'regluit.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    join(PROJECT_DIR, "frontend", "templates"),
    join(PROJECT_DIR, "frontend", "templates", "registration"),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',  
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.comments',
    'django.contrib.humanize',
    'south',
    'django_extensions',
    'regluit.frontend',
    'regluit.api',
    'regluit.core',
    'regluit.payment',
    'regluit.utils',
    'registration',
    'social_auth',
    'tastypie',
    'djcelery',
    'endless_pagination',
    'selectable',
    'regluit.frontend.templatetags',
    'regluit.payment.templatetags',
    'notification',
    'ckeditor',
    'storages',    
    # this must appear *after* django.frontend or else it overrides the 
    # registration templates in frontend/templates/registration
    'django.contrib.admin',
                            
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
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
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': join(PROJECT_DIR, 'logs', 'unglue.it.log'),
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
        '': {
            'handlers': ['file'],
            'level': 'INFO',
        }
    }
}

# django-registration
EMAIL_HOST = 'smtp.gluejar.com'
DEFAULT_FROM_EMAIL = 'notices@gluejar.com'
SERVER_EMAIL = 'notices@gluejar.com'
ACCOUNT_ACTIVATION_DAYS = 30

# django-socialauth
AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.google.GoogleOAuthBackend',
    'social_auth.backends.google.GoogleOAuth2Backend',
    'social_auth.backends.google.GoogleBackend',
    'social_auth.backends.yahoo.YahooBackend',
    'social_auth.backends.contrib.linkedin.LinkedinBackend',
    'social_auth.backends.OpenIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_ENABLED_BACKENDS = ['google', 'facebook', 'twitter']
SOCIAL_AUTH_ASSOCIATE_BY_MAIL = True
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/'

TWITTER_EXTRA_DATA = [('profile_image_url', 'profile_image_url')]

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_URL = "/accounts/logout/"

USER_AGENT = "unglue.it.bot v0.0.1 <http://unglue.it>"

SOUTH_TESTS_MIGRATE = True

AUTH_PROFILE_MODULE = "core.UserProfile"

# The amount of the transaction that Gluejar takes 
GLUEJAR_COMMISSION = 0.06
PREAPPROVAL_PERIOD = 365 # days to ask for in a preapproval
PREAPPROVAL_PERIOD_AFTER_CAMPAIGN = 90 # if we ask for preapproval time after a campaign deadline

# How many days we will try to collect on failed transactions until they are written off
RECHARGE_WINDOW = 7

GOODREADS_API_KEY = ""
GOODREADS_API_SECRET = ""

# unglue.it parameters
UNGLUEIT_MINIMUM_TARGET = '500' # in US Dollars
UNGLUEIT_LONGEST_DEADLINE = '180' # number of days allowed for a campaign
UNGLUEIT_RECOMMENDED_USERNAME = 'unglueit'

TEST_RUNNER = "djcelery.contrib.test_runner.CeleryTestSuiteRunner"
import djcelery
djcelery.setup_loader()

# set once instead of in all the templates
JQUERY_HOME = "/static/js/jquery-1.7.1.min.js"
JQUERY_UI_HOME = "/static/js/jquery-ui-1.8.16.custom.min.js"

# Mailchimp archive JavaScript URL
CAMPAIGN_ARCHIVE_JS = "http://us2.campaign-archive1.com/generate-js/?u=15472878790f9faa11317e085&fid=28161&show=5"

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

EMIT_NOTIFICATIONS_JOB = {
    "task": "regluit.core.tasks.emit_notifications",
    "schedule": datetime.timedelta(seconds=60),
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

UPDATE_ACCOUNT_STATUSES = {
    "task": "regluit.core.tasks.update_account_status",
    "schedule": crontab(day_of_month=1, hour=0, minute=0),
    "args": ()
}

# by default, in common, we don't turn any of the celerybeat jobs on -- turn them on in the local settings file

# amazon or paypal for now.
PAYMENT_PROCESSOR = 'stripelib'

# a SECRET_KEY to be used for encrypting values in core.models.Key -- you should store in settings/local.py
SECRET_KEY = ''

# by default, we are not in maintenance mode -- set True in overriding settings files for maintenance mode
# http://pypi.python.org/pypi/django-maintenancemode/
MAINTENANCE_MODE = False
# Sequence of URL path regexes to exclude from the maintenance mode.
MAINTENANCE_IGNORE_URLS = {}

class NONPROFIT:
    is_on = False
    name = 'Library Renewal'
    link = 'http://127.0.0.1:8000/donate_to_campaign/'
    
# we should suppress Google Analytics outside of production
SHOW_GOOGLE_ANALYTICS = False

# to enable uploading to S3 and integration of django-storages + django-ckeditor
# some variables to be overriddden in more specific settings files -- e.g., prod.py, 
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
AWS_STORAGE_BUCKET_NAME = ''


