from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'', include('regluit.frontend.urls')),
)
