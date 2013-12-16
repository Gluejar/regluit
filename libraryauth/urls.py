from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from . import views, models, forms
from .views import superlogin, CustomRegistrationView

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
    url(r'^accounts/register/$', CustomRegistrationView.as_view(), name='registration_register'),
    url(r'^accounts/superlogin/$', views.superlogin, name='superlogin'),
    url(r"^accounts/superlogin/welcome/$", direct_to_template, 
        {'template': 'registration/welcome.html',
            'extra_context': {'suppress_search_box': True,} 
        }), 
    url(r'^accounts/login/pledge/$',superlogin,
          {'template_name': 'registration/from_pledge.html'}),
    url(r'^accounts/login/purchase/$',superlogin,
          {'template_name': 'registration/from_purchase.html'}),
    url(r'^accounts/login/add/$',superlogin,
          {'template_name': 'registration/from_add.html'}),
    url(r'^accounts/activate/complete/$',superlogin,
          {'template_name': 'registration/activation_complete.html'}),
    url(r'^accounts/login-error/$',superlogin,
          {'template_name': 'registration/from_error.html'}),
    url(r'^accounts/edit/$', 'regluit.frontend.views.edit_user'),
    url(r"^accounts/login/welcome/$", direct_to_template, {
            'template': 'registration/welcome.html',
            'extra_context': {'suppress_search_box': True,} 
        }), 
    url(r'^socialauth/', include('social_auth.urls')),
    url('accounts/', include('email_change.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),
)
