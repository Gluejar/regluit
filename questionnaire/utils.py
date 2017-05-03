#!/usr/bin/python
import codecs
import cStringIO
import csv

from django.conf import settings
try:
    use_session = settings.QUESTIONNAIRE_USE_SESSION
except AttributeError:
    use_session = False

def split_numal(val):
    """Split, for example, '1a' into (1, 'a')
>>> split_numal("11a")
(11, 'a')
>>> split_numal("99")
(99, '')
>>> split_numal("a")
(0, 'a')
>>> split_numal("")
(0, '')
    """
    if not val:
        return 0, ''
    for i in range(len(val)):
        if not val[i].isdigit():
            return int(val[0:i] or '0'), val[i:]
    return int(val), ''

        

def numal_sort(a, b):
    """Sort a list numeric-alphabetically

>>> vals = "1a 1 10 10a 10b 11 2 2a z".split(" "); \\
... vals.sort(numal_sort); \\
... " ".join(vals)
'z 1 1a 2 2a 10 10a 10b 11'
    """
    anum, astr = split_numal(a)
    bnum, bstr = split_numal(b)
    cmpnum = cmp(anum, bnum)
    if(cmpnum == 0):
        return cmp(astr.lower(), bstr.lower())
    return cmpnum

def numal0_sort(a, b):
    """
    numal_sort on the first items in the list
    """
    return numal_sort(a[0], b[0])

def get_runid_from_request(request):
    if use_session:
        return request.session.get('runcode', None)
    else:
        return request.runinfo.run.runid

if __name__ == "__main__":
    import doctest
    doctest.testmod()

class UnicodeWriter:
    """
    COPIED from http://docs.python.org/library/csv.html example:

    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([unicode(s).encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
