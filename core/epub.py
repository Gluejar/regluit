"""
Utilities that manipulate epub files
"""

from regluit.pyepub import EPUB
from StringIO import StringIO
from django.template.loader import render_to_string

def personalize(epub_file, acq):
    output = EPUB(epub_file, "a")
    context={'acq':acq}
    part = StringIO(unicode(render_to_string('epub/datedcc_license.xhtml', context)))
    output.addpart(part, "datedcc_license.xhtml", "application/xhtml+xml", 1) #after title, we hope
    output.addmetadata('rights','%s after %s'%(acq.work.last_campaign().license_url,acq.work.last_campaign().cc_date))
    output.close()
    #output.writetodisk('testfile2.epub')
    return output