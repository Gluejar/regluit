from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template
from . import views, models

urlpatterns = patterns(
    "",
    url(r"^libraryauth/(?P<library>[^/]+)/join/$", views.join_library, name="join_library"),
    url(r"^libraryauth/(?P<library>[^/]+)/deny/$", direct_to_template, {'template':'libraryauth/denied.html'}, name="bad_library"),
    url(r"^libraryauth/list/$", direct_to_template, {
            'template':'libraryauth/list.html', 
            'extra_context':{'libraries':models.Library.objects.order_by('user__username')}
            }, name="library_list"),
    url(r'^accounts/superlogin/$', views.superlogin, name='superlogin'),
    )
