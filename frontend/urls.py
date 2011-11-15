from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.views.generic.base import TemplateView
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required

from regluit.core.models import Campaign
from regluit.frontend.views import CampaignFormView, GoodreadsDisplayView

urlpatterns = patterns(
    "regluit.frontend.views",
    url(r"^$", "home", name="home"),
    url(r"^supporter/(?P<supporter_username>.+)/$", "supporter", {'template_name': 'supporter.html'}, name="supporter"),
    url(r"^supporter2/(?P<supporter_username>.+)/$", "supporter", {'template_name': 'supporter_panel.html'}, name="supporter2"),
    url(r"^search/$", "search", name="search"),
    url(r"^privacy/$", TemplateView.as_view(template_name="privacy.html"),
        name="privacy"),
    url(r"^rightsholders/$", TemplateView.as_view(template_name="rhtools.html"),
        name="rightsholders"), 
    url(r"^rh_admin/$", "rh_admin", name="rh_admin"), 
    url(r"^faq/$", TemplateView.as_view(template_name="faq.html"),
        name="faq"), 
    url(r"^wishlist/$", "wishlist", name="wishlist"),
    url(r"^campaigns/$", ListView.as_view(
        model=Campaign,template_name="campaign_list.html", context_object_name="campaign_list")),
    url(r"^campaigns/(?P<pk>\d+)/$",CampaignFormView.as_view(), name="campaign_by_id"),
    url(r"^goodreads/$", login_required(GoodreadsDisplayView.as_view()), name="goodreads_display"),
    url(r"^goodreads/auth_cb/$", "goodreads_cb", name="goodreads_cb"),
    url(r"^goodreads/flush/$","goodreads_flush_assoc", name="goodreads_flush_assoc"),
    url(r"^goodreads/load_shelf/$","goodreads_load_shelf", name="goodreads_load_shelf"),
    url(r"^goodreads/clear_wishlist/$","clear_wishlist", name="clear_wishlist"),
    url(r"^stub/", "stub", name="stub"),
    url(r"^work/(?P<work_id>\d+)/$", "work", name="work"),
    url(r"^workstub/(?P<title>.+)/(?P<imagebase>.+)/(?P<image>.+)/(?P<author>.+)/(?P<googlebooks_id>.+)/$", "workstub", name="workstub"),
    url(r"^setup/work/(?P<work_id>\d+)/$", "work", {'action':'setup_campaign'}, name="setup_campaign"),
    url(r"^pledge/(?P<work_id>\d+)/$", "pledge", name="pledge"),
    url(r"^subjects/$", "subjects", name="subjects"),
)
