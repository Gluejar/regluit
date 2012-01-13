from zoteroconf import user_id, user_key

# http://pyzotero.readthedocs.org/en/latest/index.html

from pyzotero import zotero
zot = zotero.Zotero(user_id, user_key)
items = zot.items()
for item in items:
    print 'Author: %s | Title: %s' % (item['creators'][0]['lastName'], item['title'])