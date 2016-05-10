from django.conf.urls import patterns, url, include
from .views import SurveyView


urlpatterns = patterns('',
    url(r'^landing/(?P<nonce>\w+)/$', SurveyView.as_view(), name="landing"),
)
