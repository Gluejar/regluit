import json
import requests

def gluejar_search(q):
    """normalizes results from the google books search suitable for gluejar
    """
    results = []

    for item in googlebooks_search(q)['items']:
        v = item['volumeInfo']
        r = {'title': v.get('title', ""), 
             'description': v.get('description', ""),
             'publisher': v.get('publisher', ""),
             'googlebooks_id': item.get('id')}

        # TODO: allow multiple authors
        if v.has_key('authors') and len(v['authors']) > 0:
            r['author'] = v['authors'][0]
        else:
            r['author'] = ""
        r['isbn_10'] = None
        r['isbn_13'] = None

        # pull out isbns
        for i in v.get('industryIdentifiers', []):
            if i['type'] == 'ISBN_13':
                r['isbn_13'] = i['identifier']
            if i['type'] == 'ISBN_10':
                r['isbn_10'] = i['identifier']

        # cover image
        if v.has_key('imageLinks'):
            r['image'] = v['imageLinks'].get('thumbnail', "")
        else:
            r['image'] = ""

        access_info = item.get('accessInfo')
        if access_info:
            epub = access_info.get('epub')
            if epub and epub.get('downloadLink'):
                r['epub'] = epub['downloadLink']
            pdf = access_info.get('pdf')
            if pdf and pdf.get('downloadLink'):
                r['pdf'] = pdf['downloadLink']
        results.append(r)

    return results 


def googlebooks_search(q):
    # XXX: need to pass IP address of user in from the frontend 
    headers = {'X-Forwarded-For': '69.243.24.29'}
    r = requests.get('https://www.googleapis.com/books/v1/volumes', 
            params={'q': q}, headers=headers)
    return json.loads(r.content)
