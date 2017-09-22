from django.conf.urls import patterns, url, include
from django.core.urlresolvers import reverse
#from django.views.generic.simple import direct_to_template
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from . import views, models, forms
from .views import superlogin

# class to reproduce django 1.4 funtionality
class ExtraContextTemplateView(TemplateView):
    extra_context = None
    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        if self.extra_context is not None:
            for key, value in self.extra_context.items():
                if callable(value):
                    context[key] = value()
                else:
                    context[key] = value
        return context

urlpatterns = [
    url(r"^libraryauth/(?P<library_id>\d+)/join/$", views.join_library, name="join_library"),
    url(r"^libraryauth/(?P<library_id>\d+)/deny/$", TemplateView.as_view(template_name='libraryauth/denied.html'),  name="bad_library"),
    url(r"^libraryauth/(?P<library_id>\d+)/users/$", views.library, {'template':'libraryauth/users.html'}, name="library_users"),
    url(r"^libraryauth/(?P<library_id>\d+)/admin/$", login_required(views.UpdateLibraryView.as_view()),  name="library_admin"),
    url(r"^libraryauth/(?P<library_id>\d+)/login/$", views.login_as_library,  name="library_login"),
    url(r"^libraryauth/create/$", login_required(views.CreateLibraryView.as_view()),  name="library_create"),
    url(r"^libraryauth/list/$", ExtraContextTemplateView.as_view(
                template_name='libraryauth/list.html',
                extra_context={'libraries_to_show':'approved'}
            ),  name="library_list"),
    url(r"^libraryauth/unapproved/$", ExtraContextTemplateView.as_view(
                template_name='libraryauth/list.html', 
                extra_context={'libraries_to_show':'new'}
            ), name="new_libraries"),
    url(r'^accounts/register/$', views.CustomRegistrationView.as_view(), name='registration_register'),
    url(r'^accounts/superlogin/$', views.superlogin, name='superlogin'),
    url(r"^accounts/superlogin/welcome/$", ExtraContextTemplateView.as_view(
            template_name='registration/welcome.html',
            extra_context={'suppress_search_box': True,} 
        ) ), 
    url(r'^accounts/login/pledge/$', superlogin,
          {'template_name': 'registration/from_pledge.html'}),
    url(r'^accounts/login/purchase/$', superlogin,
          {'template_name': 'registration/from_purchase.html'}),
    url(r'^accounts/login/add/$', superlogin,
          {'template_name': 'registration/from_add.html'}),
    url(r'^accounts/activate/complete/$', superlogin,
          {'template_name': 'registration/activation_complete.html'}),
    url(r'^accounts/login-error/$', superlogin,
          {'template_name': 'registration/from_error.html'}),
    url(r'^accounts/edit/$', views.edit_user, name="edit_user"),
    url(r"^accounts/login/welcome/$", ExtraContextTemplateView.as_view(
            template_name='registration/welcome.html',
            extra_context={'suppress_search_box': True,} 
        ) ), 
    url(r'^socialauth/', include('social.apps.django_app.urls', namespace='social')),
    url('accounts/', include('email_change.urls')),
    url(r'^accounts/', include('registration.backends.model_activation.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls')),
]
