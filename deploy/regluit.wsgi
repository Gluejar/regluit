#!/usr/bin/env python

import os
import socket

import django.core.handlers.wsgi

hostname = socket.gethostname()
os.environ['DJANGO_SETTING_MODULE'] = 'regluit.settigns_%s' % hostname
application = django.core.handlers.wsgi.WSGIHander()
