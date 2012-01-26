#!/usr/bin/env python

import os

import django.core.handlers.wsgi

os.environ['CELERY_LOADER'] = 'django'
os.environ['DJANGO_SETTINGS_MODULE'] = 'regluit.settings.please'
application = django.core.handlers.wsgi.WSGIHandler()
