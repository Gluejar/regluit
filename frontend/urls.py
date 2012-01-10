from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.views.generic.base import TemplateView
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required

from regluit.core.models import Campaign
from regluit.frontend.views import CampaignFormView, GoodreadsDisplayView, LibraryThingView, PledgeView, PledgeCompleteView, PledgeCancelView, FAQView
from regluit.frontend.views import CampaignListView, DonateView, WorkListView

urlpatterns = patterns(
    "regluit.frontend.views",
    url(r"^$", "home", name="home"),
    url(r"^supporter/(?P<supporter_username>.+)/$", "supporter", {'template_name': 'supporter.html'}, name="supporter"),
    url(r"^supporter2/(?P<supporter_username>.+)/$", "supporter", {'template_name': 'supporter_panel.html'}, name="supporter2"),
    url(r"^search/$", "search", name="search"),
    url(r"^privacy/$", TemplateView.as_view(template_name="privacy.html"),
        name="privacy"),
    url(r"^terms/$", TemplateView.as_view(template_name="terms.html"),
        name="terms"),
    url(r"^rightsholders/$", "rh_tools", name="rightsholders"), 
    url(r"^rightsholders/campaign/(?P<id>\d+)/$", "manage_campaign", name="manage_campaign"), 
    url(r"^rightsholders/claim/$", "claim", name="claim"), 
    url(r"^rh_admin/$", "rh_admin", name="rh_admin"),
    url(r"^campaign_admin/$", "campaign_admin", name="campaign_admin"),    
    url(r"^faq/$", FAQView.as_view(), {'location':'faq', 'sublocation':'all'}, name="faq"), 
    url(r"^faq/(?P<location>\w*)/$", FAQView.as_view(), {'sublocation':'all'}), 
    url(r"^faq/(?P<location>\w*)/(?P<sublocation>\w*)/$", FAQView.as_view()), 
    url(r"^wishlist/$", "wishlist", name="wishlist"),
    url(r"^campaigns/(?P<pk>\d+)/$",CampaignFormView.as_view(), name="campaign_by_id"),
    url(r"^campaigns/(?P<facet>\w*)$", CampaignListView.as_view(), name='campaign_list'),
    url(r"^lists/(?P<facet>\w*)$", WorkListView.as_view(),  name='work_list'),
    url(r"^unglued/(?P<facet>\w*)$", 
        ListView.as_view( model=Campaign,template_name="campaign_list.html", context_object_name="campaign_list"), 
        name='unglued_list'),
    url(r"^goodreads/$", login_required(GoodreadsDisplayView.as_view()), name="goodreads_display"),
    url(r"^goodreads/auth/$", "goodreads_auth", name="goodreads_auth"),
    url(r"^goodreads/auth_cb/$", "goodreads_cb", name="goodreads_cb"),
    url(r"^goodreads/flush/$","goodreads_flush_assoc", name="goodreads_flush_assoc"),
    url(r"^goodreads/load_shelf/$","goodreads_load_shelf", name="goodreads_load_shelf"),
    url(r"^goodreads/clear_wishlist/$","clear_wishlist", name="clear_wishlist"),
    url(r"^stub/", "stub", name="stub"),
    url(r"^work/(?P<work_id>\d+)/$", "work", name="work"),
    url(r"^work/(?P<work_id>\d+)/librarything/$", "work_librarything", name="work_librarything"),
    url(r"^work/(?P<work_id>\d+)/goodreads/$", "work_goodreads", name="work_goodreads"),
    url(r"^work/(?P<work_id>\d+)/openlibrary/$", "work_openlibrary", name="work_openlibrary"),
    url(r"^googlebooks/(?P<googlebooks_id>.+)/$", "googlebooks", name="googlebooks"),
    #may want to deprecate the following
    url(r"^setup/work/(?P<work_id>\d+)/$", "work", {'action':'setup_campaign'}, name="setup_campaign"),
    url(r"^pledge/(?P<work_id>\d+)/$", login_required(PledgeView.as_view()), name="pledge"),
    url(r"^pledge/cancel/$", PledgeCancelView.as_view(), name="pledge_cancel"),
    url(r"^pledge/complete/$", PledgeCompleteView.as_view(), name="pledge_complete"),
    url(r"^celery/clear/$","clear_celery_tasks", name="clear_celery_tasks"),
    url(r"^subjects/$", "subjects", name="subjects"),
    url(r"^librarything/$", LibraryThingView.as_view(), name="librarything"),
    url(r"^librarything/load/$","librarything_load", name="librarything_load"),
    url(r"^donate/$", DonateView.as_view(), name="donate"),
    url('^404testing/$', direct_to_template, {'template': '404.html'}),
    url('^500testing/$', direct_to_template, {'template': '500.html'}),
    url('^robots.txt$', direct_to_template, {'template': 'robots.txt'}),
    url(r"^emailshare/$", "emailshare", name="emailshare"),
    url(r"^feedback/$", "feedback", name="feedback"),
    url(r"^feedback/thanks/$", TemplateView.as_view(template_name="thanks.html")),
    url(r"^press/$", TemplateView.as_view(template_name="press.html"),
        name="press"),
)
