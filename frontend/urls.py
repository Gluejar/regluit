from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.views.generic.base import TemplateView

urlpatterns = patterns(
    "regluit.frontend.views",
    url(r"^$", "home", name="home"),
    url(r"^supporter/(?P<supporter_username>.+)/$", "supporter", name="supporter"),
    url(r"^search/$", "search", name="search"),
    url(r"^privacy/$", TemplateView.as_view(template_name="privacy.html"),
        name="privacy"),
    url(r"^wishlist/$", "wishlist", name="wishlist"),
)
