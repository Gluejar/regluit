from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^accounts/', include('registration.backends.default.urls')),
    (r'^socialauth/', include('social_auth.urls')),
    (r'', include('regluit.frontend.urls')),

)
