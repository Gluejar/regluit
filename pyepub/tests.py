# coding=utf-8
import unittest
import urllib2 
import zipfile
import random
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
        # get an epub with no guide element
        self.epub2file2 = NamedTemporaryFile(delete=False)
        test_file_content2 = urllib2.urlopen('http://www.gutenberg.org/ebooks/2701.epub.noimages')
        self.epub2file2.write(test_file_content2.read())
        self.epub2file2.seek(0)

        
        
    def test_instantiation(self):
        epub=EPUB(self.epub2file)
        members = len(epub.namelist())
        self.assertNotEqual(epub.filename, None)
        self.assertEqual(len(epub.opf),4)
        self.assertEqual(len(epub.opf[0]),11) #metadata items
        self.assertEqual(len(epub.opf[1]),11) #manifest items
        self.assertEqual(len(epub.opf[2]),8) #spine items
        self.assertEqual(len(epub.opf[3]),3) #guide items
        # test writing
        new_epub=StringIO()
        #epub.writetodisk("test_instantiation")
        epub.writetodisk(new_epub)
        epub=EPUB(new_epub)
        self.assertEqual(len(epub.opf),4)
        self.assertEqual(members,len(epub.namelist()))
        self.assertTrue(zipfile.is_zipfile(new_epub))
        
    def test_addpart(self):
        epub=EPUB(self.epub2file,mode='a')
        members = len(epub.namelist())
        self.assertNotEqual(epub.filename, None)
        part = StringIO('<?xml version="1.0" encoding="utf-8" standalone="yes"?>')
        epub.addpart(part, "testpart.xhtml", "application/xhtml+xml", 2)
        self.assertEqual(len(epub.opf[2]),9) #spine items
        # test writing
        new_epub=StringIO()
        epub.writetodisk(new_epub)
        epub=EPUB(new_epub)
        self.assertEqual(len(epub.opf[2]),9)
        self.assertEqual(members+1,len(epub.namelist()))
        #test delete
        epub._delete("testpart.xhtml")
        new_epub=StringIO()
        epub.writetodisk(new_epub)
        new_zip = zipfile.ZipFile(new_epub)
        self.assertEqual(members,len(new_zip.namelist()))
        self.assertTrue(zipfile.is_zipfile(new_epub))

    def test_addpart_noguide(self):
        epub2=EPUB(self.epub2file2,mode='a')
        self.assertEqual(len(epub2.opf),3)
        self.assertEqual(epub2.info['guide'],None)
        num_spine_items = len(epub2.opf[2])
        uxml = u'<?xml version="1.0" encoding="utf-8" standalone="yes"?><test>VojtěchVojtíšek</test>'
        part = StringIO(unicode(uxml))
        epub2.addpart(part, "testpart.xhtml", "application/xhtml+xml", 2)
        self.assertEqual(len(epub2.opf[2]), num_spine_items +1) #spine items
        new_epub=StringIO()
        epub2.writetodisk(new_epub)
        epub2=EPUB(new_epub)
      
    def test_addmetadata(self):
        epub=EPUB(self.epub2file,mode='a')
        members = len(epub.namelist())
        epub.addmetadata('test', 'GOOD')
        self.assertIn('<dc:test>GOOD<',ET.tostring(epub.opf, encoding="UTF-8"))
        self.assertTrue(epub.opf.find('.//{http://purl.org/dc/elements/1.1/}test') is not None)
        self.assertEqual(epub.info['metadata']['test'], 'GOOD')
        # test writing
        new_epub=StringIO()
        epub.writetodisk(new_epub)
        epub=EPUB(new_epub)
        self.assertEqual(epub.info['metadata']['test'], 'GOOD')
        new_zip = zipfile.ZipFile(new_epub)
        self.assertEqual(members,len(new_zip.namelist()))
        self.assertTrue(zipfile.is_zipfile(new_epub))

    def test_new_epub(self):
        f = '%012x.epub' % random.randrange(16**12)  #random name
        epub=EPUB(f,mode='w')
        epub.addmetadata('test', 'GOOD')
        uxml = u'<?xml version="1.0" encoding="utf-8" standalone="yes"?><test>VojtěchVojtíšek</test>'
        part = StringIO(unicode(uxml))
        epub.addpart(part, "testpart.xhtml", "application/xhtml+xml", 2)
        epub.close()
        epub=EPUB(f,mode='r')
        self.assertEqual(len(epub.opf),4)
        self.assertEqual(len(epub.opf[0]),5) #metadata items
        self.assertEqual(len(epub.opf[1]),2) #manifest items
        self.assertEqual(len(epub.opf[2]),1) #spine items
        self.assertEqual(len(epub.opf[3]),0) #guide items
