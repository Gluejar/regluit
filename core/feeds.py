from django.contrib.auth.models import User
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import Atom1Feed

class SupporterWishlistFeed(Feed):
    feed_type = Atom1Feed
    def get_object(self, request, supporter):
        return get_object_or_404(User, username=supporter)
        
    def title(self, obj):
        return "Latest wishbooks for %s on unglue.it" % obj.username
        
    def description(self, obj):
        return "Latest wishbooks for %s on unglue.it" % obj.username
        
    def link(self, obj):
        return "/supporter/%s/feed/" % obj.username

    def item_title(self, item):
        return "%s" % item.title
        
    def item_link(self, item):
        return "/work/%s" % item.id

    def items(self, obj):
        return obj.wishlist.works.all().order_by('-id')[:100]    