from django.contrib.comments.models import Comment
from regluit.experimental.gutenberg import unicode_csv
import os

def output_to_csv(f, headers, rows, write_header=True, convert_values_to_unicode=True):
    """
    take rows, an iterable of dicts (and corresponding headers) and output as a CSV file to f
    """
    from unicode_csv import UnicodeDictWriter
    cw = UnicodeDictWriter(f, headers)
    if write_header:
        cw.writerow(dict([(h,h) for h in headers]))    
    for row in rows:
        if convert_values_to_unicode:
            row = dict([(k, unicode(v)) for (k,v) in row.items()])
        cw.writerow(row)
    return f

def getattr_deep(start, attr):
    """http://stackoverflow.com/a/7778877/7782 """
    obj = start
    for part in attr.split('.'):
        obj = getattr(obj, part)
    return obj

def comments(headers):
    """given a set of attributes, including deeper level values, return a dict of those attributes for the Comments"""
    return [ dict( (h, getattr_deep(c, h)) for h in headers) for c in Comment.objects.all() ]
    
def comments_csv(fname='{0}/comments.csv'.format(os.path.split(__file__)[0])):
    """write out some basic metadata about the comments"""
    f = open(fname, "wb")
    headers = ('id', 'comment', 'submit_date', 'user_name', 'content_object', 'content_object.id', 'content_object.title')
    f = output_to_csv(f, headers, comments(headers))
    f.close()
   