from django.conf.urls.defaults import *
from frontend.forms import ProfileForm

urlpatterns = patterns('',
     url(r'^accounts/activate/complete/$','django.contrib.auth.views.login',
          {'template_name': 'registration/activation_complete.html'}),
    (r'^accounts/edit/$', 'regluit.frontend.views.edit_user'),
    (r'^accounts/', include('registration.backends.default.urls')),
    (r'^socialauth/', include('social_auth.urls')),
    (r'^api/', include('regluit.api.urls')),
    ('^profiles/edit/$', 'profiles.views.edit_profile', {'form_class': ProfileForm,}),
    (r'^profiles/', include('profiles.urls')),
    (r'', include('regluit.frontend.urls')),
    (r'', include('regluit.payment.urls')),
    (r'^selectable/', include('selectable.urls')),
)
