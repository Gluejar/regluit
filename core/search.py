import json
import requests

def gluejar_search(q, user_ip='69.243.24.29'):
    """normalizes results from the google books search suitable for gluejar
    """
    results = []
    search_result=googlebooks_search(q, user_ip)
    if 'items' in search_result.keys():
        for item in search_result['items']:
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
                r['cover_image_thumbnail'] = v['imageLinks'].get('thumbnail', "")
            else:
                r['cover_image_thumbnail'] = "/static/images/generic_cover_larger.png"
    
            access_info = item.get('accessInfo')
            if access_info:
                epub = access_info.get('epub')
                if epub and epub.get('downloadLink'):
                    r['first_epub_url'] = epub['downloadLink']
                pdf = access_info.get('pdf')
                if pdf and pdf.get('downloadLink'):
                    r['first_pdf_url'] = pdf['downloadLink']
            results.append(r)
    return results 


def googlebooks_search(q, user_ip):
    # XXX: need to pass IP address of user in from the frontend 
    headers = {'X-Forwarded-For': user_ip}
    r = requests.get('https://www.googleapis.com/books/v1/volumes', 
            params={'q': q}, headers=headers)
    return json.loads(r.content)
