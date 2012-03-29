from django.conf.urls.defaults import *
from frontend.forms import ProfileForm
from django.views.generic.simple import direct_to_template
from regluit.admin import admin_site
import notification.urls

urlpatterns = patterns('',
    url(r'^accounts/activate/complete/$','django.contrib.auth.views.login',
          {'template_name': 'registration/activation_complete.html'}),
    (r'^accounts/edit/$', 'regluit.frontend.views.edit_user'),
    (r'^accounts/', include('registration.backends.default.urls')),
    (r'^socialauth/', include('social_auth.urls')),
    url(r"^accounts/login/welcome/$", direct_to_template, 
        {'template': 'registration/welcome.html',
            'extra_context': {'suppress_search_box': True,} 
        }), 
    (r'^api/', include('regluit.api.urls')),
    (r'', include('regluit.frontend.urls')),
    (r'', include('regluit.payment.urls')),
    (r'', include('regluit.experimental.urls')),
    (r'^selectable/', include('selectable.urls')),
    url(r'^admin/', include(admin_site.urls)), 
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^notification/', include(notification.urls)),
)
