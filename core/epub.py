"""
Utilities that manipulate epub files
"""

from pyepub import EPUB
from StringIO import StringIO
from django.template.loader import render_to_string

def personalize(epub_file, acq):
    output = EPUB(epub_file, "a")
    context={'acq':acq}
    part = StringIO(str(render_to_string('epub/datedcc_license.xhtml', context)))
    output.addpart(part, "datedcc_license.xhtml", "application/xhtml+xml", 1) #after title, we hope
    output.close()
    output.writetodisk('testfile2.epub')
    return output