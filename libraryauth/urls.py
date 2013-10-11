from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template
from . import views

urlpatterns = patterns(
    "",
    url(r"^libraryauth/(?P<library>[^/]+)/join/$", views.join_library, name="join_library"),
    url(r"^libraryauth/(?P<library>[^/]+)/deny/$", direct_to_template, {'template':'libraryauth/denied.html'}, name="bad_library"),
    url(r'^accounts/superlogin/$', views.superlogin, name='superlogin'),
    )
