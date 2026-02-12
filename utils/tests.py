from django.test import TestCase
from django.test.client import Client
from django.utils import unittest
from django.test.utils import override_settings
import datetime
from regluit.utils.localdatetime import now

class LocaldatetimeTest(TestCase):
    @override_settings(LOCALDATETIME_NOW=None)
    def test_LOCALDATETIME_NOW_none(self):
        from regluit.utils.localdatetime import now
        self.assertEqual(now, datetime.datetime.now)
    @override_settings(LOCALDATETIME_NOW=lambda : datetime.datetime.now() + datetime.timedelta(365))
    def test_LOCALDATETIME_NOW_year_ahead(self):
        from regluit.utils.localdatetime import now
        print now() - datetime.datetime.now()
    