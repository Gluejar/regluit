from django.conf.urls.defaults import *
from regluit.api.models import WorkResource

work_resource = WorkResource()

# (r'^api/', include('regluit.api.urls'))

urlpatterns = patterns('',
    (r'^accounts/', include('registration.backends.default.urls')),
    (r'^socialauth/', include('social_auth.urls')),
    (r'^api/', include(work_resource.urls)),
    (r'', include('regluit.frontend.urls')),

)
