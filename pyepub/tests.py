import unittest
import urllib2 
from tempfile import NamedTemporaryFile
from StringIO import StringIO
from . import EPUB
try:
    import lxml.etree as ET
except ImportError:
    import xml.etree.ElementTree as ET


class EpubTests(unittest.TestCase):

    def setUp(self):
        # get a small epub test file as a file-like object
        self.epub2file = NamedTemporaryFile(delete=False)
        test_file_content = urllib2.urlopen('http://www.hxa.name/articles/content/EpubGuide-hxa7241.epub')
        self.epub2file.write(test_file_content.read())
        self.epub2file.seek(0)
        
        
    def test_instantiation(self):
        epub=EPUB(self.epub2file)
        self.assertNotEqual(epub.filename, None)
        self.assertEqual(len(epub.opf),4)
        self.assertEqual(len(epub.opf[0]),11) #metadata items
        self.assertEqual(len(epub.opf[1]),11) #manifest items
        self.assertEqual(len(epub.opf[2]),8) #spine items
        self.assertEqual(len(epub.opf[3]),3) #guide items
        
    def test_addpart(self):
        epub=EPUB(self.epub2file,mode='a')
        self.assertNotEqual(epub.filename, None)
        part = StringIO('<?xml version="1.0" encoding="utf-8" standalone="yes"?>')
        epub.addpart(part, "testpart.xhtml", "application/xhtml+xml", 2)
        self.assertEqual(len(epub.opf[2]),9) #spine items
        
    def test_addmetadata(self):
        epub=EPUB(self.epub2file,mode='a')
        epub.addmetadata('test', 'GOOD')
        self.assertIn('<dc:test>GOOD<',ET.tostring(epub.opf, encoding="UTF-8"))
        self.assertTrue(epub.opf.find('.//{http://purl.org/dc/elements/1.1/}test') is not None)
        self.assertEqual(epub.info['metadata']['test'], 'GOOD')
        
