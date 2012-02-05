import json
import requests
import regluit.core.isbn

def gluejar_search(q, user_ip='69.243.24.29', page=1):
    """normalizes results from the google books search suitable for gluejar
    """
    results = []
    search_result=googlebooks_search(q, user_ip, page)
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
            r['isbn_13'] = None
    
            # pull out isbns
            for i in v.get('industryIdentifiers', []):
                if i['type'] == 'ISBN_13':
                    r['isbn_13'] = i['identifier']
                elif i['type'] == 'ISBN_10':
                    if not r['isbn_13'] :
                        r['isbn_13'] = regluit.core.isbn.convert_10_to_13(i['identifier'])
    
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


def googlebooks_search(q, user_ip, page):
    # XXX: need to pass IP address of user in from the frontend 
    headers = {'X-Forwarded-For': user_ip}
    start = (page - 1) * 10 
    params = {'q': q, 'startIndex': start, 'maxResults': 10}
    r = requests.get('https://www.googleapis.com/books/v1/volumes', 
            params=params, headers=headers)
    return json.loads(r.content)
