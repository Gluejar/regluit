from django.conf.urls.defaults import *
from django.conf import settings

if not settings.IS_PREVIEW:
    urlpatterns = patterns(
        "regluit.experimental.views",
        url(r"^experimental/hello", "testExperimental"),       
)
