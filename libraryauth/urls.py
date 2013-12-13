from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from . import views, models

urlpatterns = patterns(
    "",
    url(r"^libraryauth/(?P<library_id>\d+)/join/$", views.join_library, name="join_library"),
    url(r"^libraryauth/(?P<library_id>\d+)/deny/$", direct_to_template, {'template':'libraryauth/denied.html'}, name="bad_library"),
    url(r"^libraryauth/(?P<library_id>\d+)/users/$", views.library, {'template':'libraryauth/users.html'}, name="library_users"),
    url(r"^libraryauth/(?P<library_id>\d+)/admin/$", login_required(views.UpdateLibraryView.as_view()),  name="library_admin"),
    url(r"^libraryauth/(?P<library_id>\d+)/login/$", views.login_as_library,  name="library_login"),
    url(r"^libraryauth/create/$", login_required(views.CreateLibraryView.as_view()),  name="library_create"),
    url(r"^libraryauth/list/$", direct_to_template, {
            'template':'libraryauth/list.html', 
            'extra_context':{'libraries_to_show':'approved'}}, 
            name="library_list"),
    url(r"^libraryauth/unapproved/$", direct_to_template, {
            'template':'libraryauth/list.html', 
            'extra_context':{'libraries_to_show':'new'}}, 
            name="new_libraries"),
    url(r'^accounts/superlogin/$', views.superlogin, name='superlogin'),
    )
