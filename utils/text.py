import re
import sys
import unicodedata


#https://stackoverflow.com/questions/1707890/fast-way-to-filter-illegal-xml-unicode-chars-in-python
_illegal_unichrs = [(0x00, 0x08), (0x0B, 0x0C), (0x0E, 0x1F), 
                        (0x7F, 0x84), (0x86, 0x9F), 
                        (0xFDD0, 0xFDDF), (0xFFFE, 0xFFFF)] 
if sys.maxunicode >= 0x10000:  # not narrow build 
        _illegal_unichrs.extend([(0x1FFFE, 0x1FFFF), (0x2FFFE, 0x2FFFF), 
                                 (0x3FFFE, 0x3FFFF), (0x4FFFE, 0x4FFFF), 
                                 (0x5FFFE, 0x5FFFF), (0x6FFFE, 0x6FFFF), 
                                 (0x7FFFE, 0x7FFFF), (0x8FFFE, 0x8FFFF), 
                                 (0x9FFFE, 0x9FFFF), (0xAFFFE, 0xAFFFF), 
                                 (0xBFFFE, 0xBFFFF), (0xCFFFE, 0xCFFFF), 
                                 (0xDFFFE, 0xDFFFF), (0xEFFFE, 0xEFFFF), 
                                 (0xFFFFE, 0xFFFFF), (0x10FFFE, 0x10FFFF)]) 

_illegal_ranges = ["%s-%s" % (unichr(low), unichr(high)) 
                   for (low, high) in _illegal_unichrs] 
_illegal_xml_chars_RE = re.compile(u'[%s]' % u''.join(_illegal_ranges)) 

def remove_badxml(s):
    return _illegal_xml_chars_RE.sub('', s)

_ws_runs_RE = re.compile(r'[\r\n\t]+')

def sanitize_ws(s):
    return _ws_runs_RE.sub(u' ', s)

def sanitize_line(s):
    return remove_badxml(sanitize_ws(s)).strip()