from django.conf.urls.defaults import *

urlpatterns = patterns('',
     url(r'^accounts/activate/complete/$','django.contrib.auth.views.login',
          {'template_name': 'registration/activation_complete.html'}),
    (r'^accounts/', include('registration.backends.default.urls')),
    (r'^socialauth/', include('social_auth.urls')),
    (r'^api/', include('regluit.api.urls')),
    (r'', include('regluit.frontend.urls')),
    (r'', include('regluit.payment.urls'))
)
