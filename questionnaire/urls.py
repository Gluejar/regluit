# vim: set fileencoding=utf-8

from django.urls import re_path as url
from django.conf import settings
from .views import to_model


urlpatterns = [
    url(r'^landing/(?P<nonce>\w+)/$', to_model, name="landing"),
]

