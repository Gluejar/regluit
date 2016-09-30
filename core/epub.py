"""
Utilities that manipulate epub files
"""

from regluit.pyepub import EPUB, InvalidEpub
from StringIO import StringIO
from django.template.loader import render_to_string

def personalize(epub_file, acq):
    output = EPUB(epub_file, "a")
    context={'acq':acq}
    part = StringIO(unicode(render_to_string('epub/datedcc_license.xhtml', context)))
    output.addpart(part, "datedcc_license.xhtml", "application/xhtml+xml", 1) #after title, we hope
    output.addmetadata('rights','%s after %s'%(acq.work.last_campaign().license_url,acq.work.last_campaign().cc_date))
    personalized_epub= StringIO()
    output.writetodisk(personalized_epub)
    #logger.info("personalized")
    return personalized_epub

def ask_epub(epub_file, context):
    output = EPUB(epub_file, "a")
    part = StringIO(unicode(render_to_string('epub/ask.xhtml', context)))
    output.addpart(part, "ask.xhtml", "application/xhtml+xml", 1) #after title, we hope
    asking_epub= StringIO()
    output.writetodisk(asking_epub)
    return asking_epub
   
        
def ungluify(epub_file, campaign):
    output = EPUB(epub_file, "a")
    context={'campaign':campaign}
    part = StringIO(unicode(render_to_string('epub/cc_license.xhtml', context)))
    output.addpart(part, "cc_license.xhtml", "application/xhtml+xml", 1) #after title, we hope
    output.addmetadata('rights', campaign.license_url)
    output.close()
    return output

from regluit.booxtream import BooXtream
watermarker = BooXtream()

def test_epub(epub_file):
    try:
        output = EPUB(epub_file, "a")
        output.close()
        #just use Booxtream to run epubcheck
        params={
            'customername': 'epubcheck',
            'languagecode':'1033',
            'expirydays': 1,
            'downloadlimit': 1,
            'exlibris':0,
            'chapterfooter': 0,
            'disclaimer':0,
            'referenceid': 'N/A',
            'kf8mobi': False,
            'epub': True,
            }
        output.filename.seek(0)
        boox = watermarker.platform(epubfile=output.filename, **params)
        return None
    except Exception as e:
        return "error:%s" % e
