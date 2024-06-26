import unittest
import time
from urllib.request import urlopen
from tempfile import NamedTemporaryFile
from io import BytesIO
from django.conf import settings

class TestBooXtream(unittest.TestCase):
    def setUp(self):
        # get a small epub test file as a file-like object
        self.epub2file = NamedTemporaryFile(delete=False)
        test_file_content = urlopen('https://www.hxa.name/articles/content/EpubGuide-hxa7241.epub')
        self.epub2file.write(test_file_content.read())
        self.epub2file.seek(0)
        self.textfile = NamedTemporaryFile(delete=False)
        self.textfile.write(b'bad text file')
        self.textfile.seek(0)


    def _makeOne(self):
        from . import BooXtream
        manager = BooXtream()
        return manager

    def test_booxtream_errors(self):
        if settings.LOCAL_TEST:
            return
        from .exceptions import BooXtreamError
        inst = self._makeOne()
        if not settings.BOOXTREAM_API_KEY:
            return
        with self.assertRaises(BooXtreamError) as cm:
            inst.platform()
        self.assertIn('expirydays not set', str(cm.exception))
        params = {
            'customername': 'Jane Test',
            'languagecode':'1043',
            'expirydays': 1,
            'downloadlimit': 3,
            'exlibris':1,
            'chapterfooter':1,
            'disclaimer':1,
            'referenceid':'bad_file_check'
            }
        with self.assertRaises(BooXtreamError) as cm:
            inst.platform(epubfile=self.textfile, **params)



    def test_booxtream_good(self):
        inst = self._makeOne()
        params = {
            'customeremailaddress':'jane@example.com',
            'customername': 'Jane Test',
            'languagecode':'1043',
            'expirydays': 1,
            'downloadlimit': 3,
            'exlibris':1,
            'chapterfooter':1,
            'disclaimer':1,
            }
        params['referenceid'] = 'order' + str(time.time())
        boox = inst.platform(epubfile=self.epub2file, **params)
        self.assertRegexpMatches(boox.download_link_epub, 'download.booxtream.com/')
        self.assertFalse(boox.expired)
        self.assertEqual(boox.downloads_remaining, 3)

        # make sure it works with an in-memory file
        self.epub2file.seek(0)
        in_mem_epub = BytesIO()
        in_mem_epub.write(self.epub2file.read())
        in_mem_epub.seek(0)
        boox2 = inst.platform(epubfile=in_mem_epub, **params)
        self.assertRegexpMatches(boox2.download_link_epub, 'download.booxtream.com/')
