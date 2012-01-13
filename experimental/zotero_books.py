from zoteroconf import user_id, user_key

from itertools import islice
from functools import partial

from pyzotero.zotero import Zotero
import logging
logger = logging.getLogger(__name__)

class Zotero2(Zotero):
    def __init__(self, user_id = None, user_key = None):
        self.__params = {}
        super(Zotero2,self).__init__(user_id,user_key)
    def set_parameters(self, **kwargs):
        self.__params.update(kwargs)
    def _to_iterator(self, f, *args, **kwargs):
        current_start = self.__params.get("start", 0)
        params = self.__params.copy()
        
        params["start"] = current_start
        more_items = True
        
        while more_items:
            self.add_parameters(**params)
            items = f(*args,**kwargs)
            for item in items:
                yield item
            params["start"] += len(items)
            if len(items) == 0:
                more_items = False
    def __getattribute__(self, name):
        if name in ['items','item','top','children','tag_items', 'group_items','group_top',
                    'group_item','group_item_children', 'group_items_tag',
                    'group_collection_items', 'group_collection_item',
                    'group_collection_top','collection_items','get_subset',
                    'collections','collections_sub','group_collections',
                    'group_collection',
                    'groups','tags','item_tags','group_tags','group_item_tags']:
            #f = super(Zotero2,self).items
            f = getattr(super(Zotero2,self),name)
            #return self._to_iterator(f)
            return partial(self._to_iterator,f)
        else:
            return super(Zotero2,self).__getattribute__(name)
    #def items(self):
    #    f = super(Zotero2,self).items
    #    return self._to_iterator(f)
    #def items0(self):
    #    current_start = self._params.get("start", 1)
    #    params = self._params
    #    
    #    params["start"] = current_start
    #    more_items = True
    #    
    #    while more_items:
    #        self.add_parameters(**params)
    #        items = super(Zotero2,self).items()
    #        for item in items:
    #            yield item
    #        params["start"] += len(items)
    #        if len(items) == 0:
    #            more_items = False

class MyZotero(Zotero2):
    def __init__(self, user_id=user_id, user_key=user_key):
        super(MyZotero,self).__init__(user_id,user_key)
    def items_in_unglue_it_collection(self):
        return self.collection_items('3RKQ23IP')
    def compare_keys(self,max,pagesize1,pagesize2):
        set1 = self.item_keys(max,pagesize1)
        set2 = self.item_keys(max,pagesize2)
        
        print "length: ", len(set1), len(set2)
        print set1 ^ set2
    def item_keys(self, max, page_size):
        self.set_parameters(limit=page_size)
        items = self.items()
        item_set = set()
        for (i, item) in enumerate(islice(items,max)):
            item_set.add((item["group_id"], item["key"], item["title"]))
            print i, (item["group_id"], item["key"], item["title"])
        return item_set
    def get_all_items(self):
        print len(self.item_keys(5000,99))
    def get_books(self,max=10000):
        self.set_parameters(sort="type", itemType="book")
        items = self.items()
        for (i, item) in enumerate(islice(items,max)):
            if item.get("itemType") == 'book':
                yield {'group_id':item["group_id"], 'key':item["key"], 'title':item["title"],
                       'itemType':item.get("itemType"), 'isbn':item.get("ISBN", None)}      
    def upload_to_unglue_it(self,unglueit_user_name, max):
        from regluit.core import bookloader
        from django.contrib.auth.models import User
        
        user = User.objects.get(username=unglueit_user_name)
        books = self.get_books(max=max)
        for book in books:
            try:
                isbn = book['isbn']
                if isbn:
                    edition = bookloader.add_by_isbn(isbn)
                    # let's not trigger too much traffic to Google books for now
                    regluit.core.tasks.populate_edition.delay(edition)
                    user.wishlist.add_work(edition.work, 'zotero')
                    logger.info("Work with isbn %s added to wishlist.", isbn)
            except Exception, e:
                logger.info ("error adding ISBN %s: %s", isbn, e)            


def get_unglue_collection():
    zot = MyZotero()
    #zot.compare_keys(24,7,3)
    to_unglue = list(zot.items_in_unglue_it_collection())
    print len(to_unglue), [item["title"] for item in to_unglue]
    for (i,b) in enumerate(zot.get_books(300)):
        print b
    #zot.upload_to_unglue_it('RaymondYee',5000)
    #print zot.get_all_items()
        
def hello_world():
    zot = Zotero(user_id, user_key)
    items = zot.items()
    for item in items:
        print 'Author: %s | Title: %s' % (item['creators'][0]['lastName'], item['title'])
    
        
if __name__ == '__main__':
    hello_world()


