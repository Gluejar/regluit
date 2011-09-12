from django.conf.urls.defaults import *

urlpatterns = patterns(
    "regluit.frontend.views",
    url(r"^$", "home", name="home"),
    url(r"^user/(?P<username>.+)/$", "user", name="user"),
)
