# scrape my amazon wishlist

import requests
import lxml.html
from lxml.cssselect import CSSSelector

def net_text(e):
    children = e.getchildren()
    if len(children) > 0 :
        return "".join(map(net_text,children))
    else:
        return e.text if e.text is not None else ''
    
wishlist_id = '1U5EXVPVS3WP5'
url = "http://www.amazon.com/wishlist/%s/ref=cm_wl_act_print_o?_encoding=UTF8&layout=standard-print&disableNav=1&visitor-view=1&items-per-page=500&page=1" % (wishlist_id)
r = requests.get(url)
html = lxml.html.fromstring(r.content.decode("UTF-8"))

sel = CSSSelector('#itemsTable tr')
elems = sel(html)

# just realized no isbn in print version....need to do more work

for (i, tr) in enumerate(elems):
    print i,
    for td in tr.findall('td'):
        print net_text(td),
    print 
        
