#!/usr/bin/env python

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "regluit.settings.prod")
os.environ['CELERY_LOADER'] = 'django'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()