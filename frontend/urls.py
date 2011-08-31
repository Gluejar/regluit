from django.conf.urls.defaults import *

urlpatterns = patterns(
    "regluit.frontend.views",
    url(r"^$", "home", name="home"),
)
