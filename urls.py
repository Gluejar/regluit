from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^accounts/', include('registration.backends.default.urls')),
    (r'', include('regluit.frontend.urls')),
)
