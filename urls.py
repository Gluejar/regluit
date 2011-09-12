from django.conf.urls.defaults import *
from tastypie.api import Api
from regluit.api.models import WorkResource, EditionResource, CampaignResource, AuthorResource, SubjectResource

v1_api = Api(api_name='v1')  # how set api_name to None?  Don't think there is a way...
v1_api.register(WorkResource())
v1_api.register(EditionResource())
v1_api.register(CampaignResource())
v1_api.register(AuthorResource())
v1_api.register(SubjectResource())

# (r'^api/', include('regluit.api.urls'))

urlpatterns = patterns('',
    (r'^accounts/', include('registration.backends.default.urls')),
    (r'^socialauth/', include('social_auth.urls')),
    (r'^api/', include(v1_api.urls)),
    (r'', include('regluit.frontend.urls')),

)
