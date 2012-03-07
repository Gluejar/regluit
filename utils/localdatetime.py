"""
Utility to return datetime.datetime.utcnow() by default but allows for a custom utcnow() (e.g., for testing)

>>> import regluit
>>> from regluit.utils.localdatetime import now
>>> now()
datetime.datetime(2012, 3, 8, 14, 0, 35, 409270)
>>> now()
datetime.datetime(2012, 3, 8, 14, 0, 36, 985271)
>>> n = now()
>>> n
datetime.datetime(2012, 3, 8, 14, 1, 54, 650679)
>>> regluit.utils.localdatetime._now = lambda: n
>>> now()
datetime.datetime(2012, 3, 8, 14, 1, 54, 650679)
>>> now()
datetime.datetime(2012, 3, 8, 14, 1, 54, 650679)
>>> now()


"""

import datetime
import django

# for Django 1.3.x, return a timestamp naive now()
# for Django 1.4 should switch to django.utils.timezone.now()
# see https://code.djangoproject.com/browser/django/trunk/django/utils/timezone.py?rev=17642#L232

try:
    _now = django.utils.timezone.now
except AttributeError, e:
    _now = datetime.datetime.now
    
now = lambda: _now()

# provide a replacement for datetime.date.today()
# this will be timezone naive -- is that what we really want?

date_today = lambda: _now().date()


