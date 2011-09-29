import json
import requests

def gluejar_search(q):
    """normalizes results from the google books search suitable for gluejar
    """
    results = []

    for item in googlebooks_search(q)['items']:
        # TODO: better to think in terms of editions with titles 
        # instead of titles with names?
        v = item['volumeInfo']
        r = {'title': v.get('title', ""), 
             'description': v.get('description', ""),
             'publisher': v.get('publisher', ""),
             'google_id': item.get('selfLink')}

        # TODO: allow multiple authors
        if v.has_key('authors') and len(v['authors']) > 0:
            r['author'] = v['authors'][0]
        else:
            r['author'] = ""

        # pull out isbns
        for i in v.get('industryIdentifiers', []):
            if i['type'] == 'ISBN_13':
                r['isbn_13'] = i['identifier']
            if i['type'] == 'ISBN_10':
                r['isbn_10'] = i['identifier']

        # cover image
        if v.has_key('imageLinks'):
            r['image'] = v['imageLinks'].get('smallThumbnail', "")
        else:
            r['image'] = ""

        results.append(r)

    return results 


def googlebooks_search(q):
    # XXX: need to pass IP address of user in from the frontend 
    headers = {'X-Forwarded-For': '69.243.24.29'}
    r = requests.get('https://www.googleapis.com/books/v1/volumes', 
            params={'q': q}, headers=headers)
    return json.loads(r.content)
