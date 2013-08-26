import unittest
import time

# uses settings.BOOXTREAM_TEST_EPUB
from . import settings

class TestBooXtream(unittest.TestCase):
    def _makeOne(self):
        from . import BooXtream
        manager = BooXtream()
        return manager

    def test_booxtream_errors(self):
        from .exceptions import BooXtreamError
        inst = self._makeOne()
        with self.assertRaises(BooXtreamError) as cm:
            inst.platform()
        self.assertIn( 'expirydays not set',str(cm.exception))


    def test_booxtream_good(self):
        inst = self._makeOne()
        params={
            'customeremailaddress':'jane@example.com',
            'customername': 'Jane Test',
            'languagecode':'1043',
            'expirydays': 1,
            'downloadlimit': 3,
            'exlibris':1,
            'chapterfooter':1,
            'disclaimer':1,
            }
        params['referenceid']= 'order'+str(time.time())
        epubfile= open(settings.BOOXTREAM_TEST_EPUB)
        boox=inst.platform(epubfile=epubfile, **params)
        self.assertRegexpMatches(boox.download_link_epub,'download.booxtream.com/')
        self.assertFalse(boox.expired)
        self.assertEqual(boox.downloads_remaining,3)