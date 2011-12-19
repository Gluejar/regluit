#!/usr/bin/env python

import re
import json
import fileinput

import requests

def match():
    for line in fileinput.input():
        j = json.loads(line)
        authors = j['authors']
        title = j['title']
        print googlebooks_id(title, authors)

def google_search(title, authors, no_matches):
    headers = {'X-Forwarded-For': '69.243.24.29'}
    # the title and author are intentionally not fielded
    params = {
        'q': title,
        'key': 'AIzaSyBE36z7o6NUafIWcLEB8yk2I47-8_5y1_0'
    }
    for author in authors:
        params['q'] += ' ' + norm_author(author)
    r = requests.get('https://www.googleapis.com/books/v1/volumes', 
            params=params, headers=headers)
    results = json.loads(r.content)
    if not results.has_key('totalItems'):
        print >> no_matches, "missing totalItems for %s" % r.url
        print >> no_matches, r.content
        return "missing totalItems"
    if results['totalItems'] == 0:
        return "no search results"
        return None
    for item in results['items']:
        g_title = item['volumeInfo'].get('title', '')
        g_title += ' ' + item['volumeInfo'].get('subtitle', '')
        g_authors = item['volumeInfo'].get('authors', [])
        if norm_title(g_title) == norm_title(title) and \
                authors_equal(g_authors, authors):
           return item['id']

    msg = "%s\t%s\t%s" % (title, authors, r.url)
    print >> no_matches, msg.encode('utf-8')
    print >> no_matches, r.content
    print >> no_matches, ""
    return "no match"

def norm_title(t):
    t = t.lower()
    t = re.sub('^((the)|(a)|(an)) ', '', t)
    t = re.sub('[^A-Za-z]', '', t)
    return t[0:15]

def authors_equal(a, b):
    if len(a) == 0 and len(b) == 0:
        return True
    if len(a) == 0 or len(b) == 0:
        return False

    a = map(extra_norm_author, a)
    b = map(extra_norm_author, b)

    return len(set(a) & set(b)) > 0

def extra_norm_author(a):
    a = norm_author(a)
    a = a.lower()
    a = re.sub('[^a-z]', '', a)
    return a

def norm_author(a):
    parts = a.split(',')
    parts = [p.strip() for p in parts]
    if len(parts) > 1 and re.search('\d\d', parts[-1]):
        parts.pop(-1)
    parts.append(parts.pop(0))
    a = ' '.join(parts)
    a = re.sub('\(.+?\)', '', a)
    a = re.sub('  +', ' ', a)
    a = re.sub('[^A-Za-z \-]', '', a)
    return a

if __name__ == "__main__":
    googlebooks_ids()
