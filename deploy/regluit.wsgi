#!/usr/bin/env python

import os

import django.core.handlers.wsgi

os.environ['DJANGO_SETTINGS_MODULE'] = 'regluit.settings.prod'
application = django.core.handlers.wsgi.WSGIHandler()
