from zoteroconf import user_id, user_key

# http://pyzotero.readthedocs.org/en/latest/index.html

from pyzotero import zotero
zot = zotero.Zotero(user_id, user_key)
items = zot.top()
for item in items:
    #print item
    try:
        print 'Author: %s | Title: %s' % (item['creators'][0]['lastName'] if item['creators'] else '', item['title'])
    except Exception, e:
        print "Error: %s " % (e)