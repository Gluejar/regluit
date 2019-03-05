"""
Utilities that manipulate pdf files
"""
import logging
from io import BytesIO
from StringIO import StringIO
from tempfile import NamedTemporaryFile

import requests
from xhtml2pdf import pisa             # import python module
from PyPDF2 import PdfFileMerger, PdfFileReader
from PyPDF2.utils import PdfReadError
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)

# Utility function
def ask_pdf(context={}):
    ask_html = StringIO(unicode(render_to_string('pdf/ask.html', context)))
    # open output file for writing (truncated binary)
    resultFile = StringIO()

    # convert HTML to PDF
    pisaStatus = pisa.CreatePDF(
        src=ask_html,                # the HTML to convert
        dest=resultFile,           # file  to recieve result
    )
    #  True on success and False on errors
    assert pisaStatus.err == 0
    return resultFile

def pdf_append(file1, file2, file_out):
    merger = PdfFileMerger(strict=False)
    merger.append(file1)
    merger.append(file2)
    merger.write(file_out)
    merger.close()

def test_pdf(pdf_file):
    temp = None
    try:
        if isinstance(pdf_file, (str, unicode)):
            if pdf_file.startswith('http:') or pdf_file.startswith('https:'):
                temp = NamedTemporaryFile(delete=False)
                test_file_content = requests.get(pdf_file).content
                temp.write(test_file_content)
                temp.seek(0)
            else:
                # hope it's already a file
                temp = open(pdf_file, mode='rb')
        else:
            pdf_file.seek(0)
            temp = pdf_file
        try:
            PdfFileReader(temp)
            success = True
        except:
            success = False
        return success
    except Exception:
        pdf_file = unicode(pdf_file)
        logger.exception('error testing a pdf: %s' % pdf_file[:100])
        return False

def staple_pdf(urllist, user_agent=settings.USER_AGENT):
    merger = PdfFileMerger(strict=False)
    s = requests.Session()
    for url in urllist:
        try:
            response = s.get(url, headers={"User-Agent": user_agent})
        except requests.exceptions.ConnectionError:
            logger.error("Error getting url: %s", url)
            return None
        if response.status_code == 200:
            try:
                merger.append(BytesIO(response.content))
            except PdfReadError:
                logger.error("error reading pdf url: %s", url)
                return None
        else:
            return None
    out = BytesIO()
    try:
        merger.write(out)
    except PdfReadError:
        logger.error("error writing pdf url: %s", url)
        return None
    return out

def test_test_pdf():
    assert(test_pdf(settings.TEST_PDF_URL))
    temp = NamedTemporaryFile(delete=False)
    test_file_content = requests.get(settings.TEST_PDF_URL).content
    temp.write(test_file_content)
    assert test_pdf(temp)
    temp.close()
