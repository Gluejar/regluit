from django.conf.urls.defaults import *
from .views import SurveyView


urlpatterns = patterns('',
    url(r'^landing/(?P<nonce>\w+)/$', SurveyView.as_view(), name="landing"),
)
