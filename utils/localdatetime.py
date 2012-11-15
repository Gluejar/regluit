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

DST handled:

>>> ptz = pytz.timezone('America/Los_Angeles')
>>> make_naive(datetime.datetime(2012,03,11,10,tzinfo=utc), ptz)
datetime.datetime(2012, 3, 11, 3, 0)
>>> make_naive(datetime.datetime(2012,03,11,9,tzinfo=utc), ptz)
datetime.datetime(2012, 3, 11, 1, 0)

>>> make_aware(datetime.datetime(2012,11,4,1,30), ptz)
Traceback (most recent call last):
  File "<console>", line 1, in <module>
  File "/Users/raymondyee/C/src/Gluejar/regluit/utils/localdatetime.py", line 90, in make_aware
    return timezone.localize(value, is_dst=None)
  File "/Users/raymondyee/.virtualenvs/regluit/lib/python2.7/site-packages/pytz/tzinfo.py", line 349, in localize
    raise AmbiguousTimeError(dt)
AmbiguousTimeError: 2012-11-04 01:30:00


"""

import pytz
import datetime
import django
from django.conf import settings

# for Django 1.3.x, return a timestamp naive now()
# for Django 1.4 should switch to django.utils.timezone.now()
# see https://code.djangoproject.com/browser/django/trunk/django/utils/timezone.py?rev=17642#L232

def now():
    if hasattr(settings, 'LOCALDATETIME_NOW') and settings.LOCALDATETIME_NOW is not None:
        return settings.LOCALDATETIME_NOW()
    else:
        try:
            return django.utils.timezone.now()
        except AttributeError, e:
            return datetime.datetime.now()    
    
# provide a replacement for datetime.date.today()
# this will be timezone naive -- is that what we really want?

def date_today():
    return now().date()

# borrow a lot of the routines/code that will be in Django 1.4+ django.utils.timezone
# https://code.djangoproject.com/browser/django/trunk/django/utils/timezone.py

utc = pytz.utc

def get_default_timezone():
    return pytz.timezone(settings.TIME_ZONE)
    
def is_aware(value):
    """
    Determines if a given datetime.datetime is aware.

    The logic is described in Python's docs:
    http://docs.python.org/library/datetime.html#datetime.tzinfo
    """
    return value.tzinfo is not None and value.tzinfo.utcoffset(value) is not None

def is_naive(value):
    """
    Determines if a given datetime.datetime is naive.

    The logic is described in Python's docs:
    http://docs.python.org/library/datetime.html#datetime.tzinfo
    """
    return value.tzinfo is None or value.tzinfo.utcoffset(value) is None

def make_aware(value, timezone):
    """
    Makes a naive datetime.datetime in a given time zone aware.
    """
    if hasattr(timezone, 'localize'):
        # available for pytz time zones
        return timezone.localize(value, is_dst=None)
    else:
        # may be wrong around DST changes
        return value.replace(tzinfo=timezone)

def make_naive(value, timezone):
    """
    Makes an aware datetime.datetime naive in a given time zone.
    """
    value = value.astimezone(timezone)
    if hasattr(timezone, 'normalize'):
        # available for pytz time zones
        value = timezone.normalize(value)
    return value.replace(tzinfo=None)

def isoformat(value):
    """
    if value is naive, assume it's in the default_timezone
    """
    if is_naive(value):
        return make_aware(value, get_default_timezone()).isoformat()
    else:
        return value.isoformat()

def zuluformat(value):
    """format value in zulu format -- e.g., 2012-03-26T17:47:22.654449Z"""
    return "{0}Z".format(as_utc_naive(value).isoformat())

def as_utc_naive(value):
    """
    if value is naive, assume it's in the default time zone, then convert to UTC but make naive 
    """
    if is_naive(value):
        return make_naive(make_aware(value, get_default_timezone()), utc)
    else:
        return make_naive(value, utc)
    
def as_default_timezone_naive(value):
    """
    if value is naive, assume it's in UTC and convert to the default tz and make it naive
    """
    if is_naive(value):
        return make_naive(make_aware(value, utc), get_default_timezone())
    else:
        return make_naive(value, get_default_timezone())    
