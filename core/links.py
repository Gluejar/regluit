ID_URLS = {
    'goog': u'https://books.google.com/books?id={}',
    'olwk': u'https://openlibrary.org{}',
    'gdrd': u'https://www.goodreads.com/book/show/{}',
    'ltwk': u'https://librarything.com/work/{}',
    'oclc': u'https://www.worldcat.org/oclc/{}',
    'doi': u'https://doi.org/{}',
    'gtbg': u'https://gutenberg.org/ebooks/{}',
    'glue': u'https://unglue.it/work/{}',
}

def id_url(id_type, id_value):
    url_string = ID_URLS.get(id_type, None)
    if url_string and id_value:
        return url_string.format(id_value)
    else:
        return ''