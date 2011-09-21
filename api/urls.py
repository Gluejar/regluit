from django.conf.urls.defaults import *
from tastypie.api import Api

from regluit.api import resources

v1_api = Api(api_name='v1')
v1_api.register(resources.UserResource())
v1_api.register(resources.WorkResource())
v1_api.register(resources.EditionResource())
v1_api.register(resources.EditionCoverResource())
v1_api.register(resources.CampaignResource())
v1_api.register(resources.AuthorResource())
v1_api.register(resources.SubjectResource())
v1_api.register(resources.WishlistResource())

urlpatterns = patterns('',
    (r'^', include(v1_api.urls)),
)
