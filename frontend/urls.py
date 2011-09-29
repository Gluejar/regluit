from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns(
    "regluit.frontend.views",
    url(r"^$", "home", name="home"),
    url(r"^supporter/(?P<supporter_username>.+)/$", "supporter", name="supporter"),
    url(r"^search/$", "search", name="search"),
    url(r"^privacy/$", direct_to_template, {"template": "privacy.html"},
        name="privacy"),
)
