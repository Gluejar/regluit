#!/bin/bash

django-admin.py celeryd --loglevel=INFO &
django-admin.py celerybeat -l INFO &
django-admin.py runserver 0.0.0.0:8000
