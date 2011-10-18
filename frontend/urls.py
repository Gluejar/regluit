from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.views.generic.base import TemplateView
from django.views.generic import ListView, DetailView

from regluit.core.models import Campaign
from regluit.frontend.views import CampaignFormView

urlpatterns = patterns(
    "regluit.frontend.views",
    url(r"^$", "home", name="home"),
    url(r"^supporter/(?P<supporter_username>.+)/$", "supporter", name="supporter"),
    url(r"^search/$", "search", name="search"),
    url(r"^privacy/$", TemplateView.as_view(template_name="privacy.html"),
        name="privacy"),
    url(r"^rightsholders/$", TemplateView.as_view(template_name="rhtools.html"),
        name="rightsholders"), 
    url(r"^wishlist/$", "wishlist", name="wishlist"),
    url(r"^campaigns/$", ListView.as_view(
        model=Campaign,template_name="campaign_list.html", context_object_name="campaign_list")),
    url(r"^campaigns/(?P<pk>\d+)/$",CampaignFormView.as_view(), name="campaign_by_id")
)
