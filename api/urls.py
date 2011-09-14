from django.conf.urls.defaults import *
from tastypie.api import Api

from regluit.api.models import UserResource, WorkResource, EditionResource, CampaignResource, AuthorResource, SubjectResource, EditionCoverResource, WishlistResource

v1_api = Api(api_name='v1')  # how set api_name to None so that we don't get URIs like /api/v1 but more like /api/ Don't think there is a way...
v1_api.register(UserResource())
v1_api.register(WorkResource())
v1_api.register(EditionResource())
v1_api.register(EditionCoverResource())
v1_api.register(CampaignResource())
v1_api.register(AuthorResource())
v1_api.register(SubjectResource())
v1_api.register(WishlistResource())

urlpatterns = patterns('',
    url(r'^editions/$', 'regluit.api.views.editions', name="editions"),
    url(r'^isbn/(?P<isbn>\w+)/$','regluit.api.views.isbn', name="isbn"),
    (r'^', include(v1_api.urls)),
)
