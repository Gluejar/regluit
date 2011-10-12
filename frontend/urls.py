from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.views.generic.base import TemplateView
from django.views.generic import ListView, DetailView

from regluit.core.models import Campaign
from regluit.frontend.views import CampaignDetailView, RYLearnView, CampaignFormView, CampaignFormView2

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
    url(r"^rylearn0/$", "rylearn0", name="rylearn0"),
    url(r"^rylearn1/$", direct_to_template, {'template': 'rylearn.html', 'extra_context':{'message':'hello there from rylearn1'}}, name="rylearn"),
    url(r"^rylearn2/$", RYLearnView.as_view(),name="rylearn2"),
    url(r"^campaigns/$", ListView.as_view(
        model=Campaign,template_name="campaign_list.html", context_object_name="campaign_list")),
    url(r"^campaigns/(?P<pk>\d+)/$",CampaignFormView2.as_view(), name="campaign_by_id")
)

# url(r'^campaigns/(?P<pk>\d+)/$', CampaignDetailView.as_view(), name="campaign_by_id"),
# url(r"^campaigns/(?P<pk>\d+)/$","campaign_detail", name="campaign_by_id")