from django.conf.urls.defaults import *

urlpatterns = patterns(
    'regluit.frontend.views',
    url(r'^$', 'home', name='home'),
    url(r'^supporter/(?P<supporter_username>.+)/$', 'supporter', name='supporter'),
    url(r'^privacy$', 'textpage', {'page': 'privacy'}, name='privacy'),
)
