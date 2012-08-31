from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.views.generic.base import TemplateView
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.conf import settings

from regluit.core.feeds import SupporterWishlistFeed
from regluit.core.models import Campaign
from regluit.frontend.views import GoodreadsDisplayView, LibraryThingView, PledgeView, PledgeCompleteView, PledgeCancelView, PledgeRechargeView, FAQView
from regluit.frontend.views import CampaignListView, DonateView, WorkListView, UngluedListView, InfoPageView, InfoLangView, DonationView

urlpatterns = patterns(
    "regluit.frontend.views",
    url(r"^$", "home", name="home"),
    url(r"^landing/$", "home", {'landing': True}, name="landing"),
    url(r"^next/$", "next", name="next"),
    url(r"^supporter/(?P<supporter_username>[^/]+)/$", "supporter", {'template_name': 'supporter.html'}, name="supporter"),
    url(r"^search/$", "search", name="search"),
    url(r"^privacy/$", TemplateView.as_view(template_name="privacy.html"),
        name="privacy"),
    url(r"^terms/$", TemplateView.as_view(template_name="terms.html"),
        name="terms"),
    url(r"^rightsholders/$", "rh_tools", name="rightsholders"), 
    url(r"^rightsholders/campaign/(?P<id>\d+)/$", "manage_campaign", name="manage_campaign"), 
    url(r"^rightsholders/edition/(?P<work_id>\d*)/(?P<edition_id>\d*)$", "new_edition",{'by': 'rh'}, name="rh_edition"),
    url(r"^rightsholders/claim/$", "claim", name="claim"), 
    url(r"^rh_admin/$", "rh_admin", name="rh_admin"),
    url(r"^campaign_admin/$", "campaign_admin", name="campaign_admin"),    
    url(r"^faq/$", FAQView.as_view(), {'location':'faq', 'sublocation':'all'}, name="faq"), 
    url(r"^faq/(?P<location>\w*)/$", FAQView.as_view(), {'sublocation':'all'}, name="faq_location"), 
    url(r"^faq/(?P<location>\w*)/(?P<sublocation>\w*)/$", FAQView.as_view()), 
    url(r"^wishlist/$", "wishlist", name="wishlist"),
    url(r"^campaigns/(?P<facet>\w*)$", CampaignListView.as_view(), name='campaign_list'),
    url(r"^lists/(?P<facet>\w*)$", WorkListView.as_view(),  name='work_list'),
    url(r"^unglued/(?P<facet>\w*)$", UngluedListView.as_view(),  name='unglued_list'),
    url(r"^goodreads/auth/$", "goodreads_auth", name="goodreads_auth"),
    url(r"^goodreads/auth_cb/$", "goodreads_cb", name="goodreads_cb"),
    url(r"^goodreads/flush/$","goodreads_flush_assoc", name="goodreads_flush_assoc"),
    url(r"^goodreads/load_shelf/$","goodreads_load_shelf", name="goodreads_load_shelf"),
    url(r"^goodreads/shelves/$","goodreads_calc_shelves", name="goodreads_calc_shelves"),
    url(r"^stub/", "stub", name="stub"),
    url(r"^work/(?P<work_id>\d+)/$", "work", name="work"),
    url(r"^work/(?P<work_id>\d+)/preview/$", "work", {'action': 'preview'}, name="work_preview"),
    url(r"^work/(?P<work_id>\d+)/acks/$", "work", {'action': 'acks'}, name="work_acks"),
    url(r"^work/(?P<work_id>\d+)/lockss/$", "lockss", name="lockss"),
    url(r"^work/\d+/acks/images/(?P<file_name>[\w\.]*)$", "static_redirect_view",{'dir': 'images'}), 
    url(r"^work/(?P<work_id>\d+)/librarything/$", "work_librarything", name="work_librarything"),
    url(r"^work/(?P<work_id>\d+)/goodreads/$", "work_goodreads", name="work_goodreads"),
    url(r"^work/(?P<work_id>\d+)/openlibrary/$", "work_openlibrary", name="work_openlibrary"),
    url(r"^new_edition/(?P<work_id>)(?P<edition_id>)$", "new_edition", name="new_edition"),
    url(r"^new_edition/(?P<work_id>\d*)/(?P<edition_id>\d*)$", "new_edition", name="new_edition"),
    url(r"^googlebooks/(?P<googlebooks_id>.+)/$", "googlebooks", name="googlebooks"),
    url(r"^donation/$", login_required(DonationView.as_view()), name="donation"),
    url(r"^pledge/(?P<work_id>\d+)/$", login_required(PledgeView.as_view()), name="pledge"),
    url(r"^pledge/cancel/(?P<campaign_id>\d+)$", login_required(PledgeCancelView.as_view()), name="pledge_cancel"),
    url(r"^pledge/complete/$", login_required(PledgeCompleteView.as_view()), name="pledge_complete"),
    url(r"^pledge/modify/(?P<work_id>\d+)$", login_required(PledgeView.as_view()), name="pledge_modify"),
    url(r"^pledge/recharge/(?P<work_id>\d+)$", login_required(PledgeRechargeView.as_view()), name="pledge_recharge"),
    url(r"^subjects/$", "subjects", name="subjects"),
    url(r"^librarything/$", LibraryThingView.as_view(), name="librarything"),
    url(r"^librarything/load/$","librarything_load", name="librarything_load"),
    url('^404testing/$', direct_to_template, {'template': '404.html'}),
    url('^500testing/$', direct_to_template, {'template': '500.html'}),
    url('^robots.txt$', direct_to_template, {'template': 'robots.txt', 'mimetype': 'text/plain'}),
    url(r"^emailshare/(?P<action>\w*)/?$", "emailshare", name="emailshare"),
    url(r"^feedback/$", "feedback", name="feedback"),
    url(r"^feedback/thanks/$", TemplateView.as_view(template_name="thanks.html")),
    url(r"^press/$", TemplateView.as_view(template_name="press.html"),
        name="press"),
    url(r"^about/$", TemplateView.as_view(template_name="about.html"),
        name="about"),
    url(r"^comments/$", "comment", name="comment"),
    url(r"^info/(?P<template_name>[\w\.]*)$", InfoPageView.as_view()), 
    url(r"^info/languages/(?P<template_name>[\w\.]*)$", InfoLangView.as_view()), 
    url(r'^supporter/(?P<supporter>[^/]+)/feed/$', SupporterWishlistFeed()),
    url(r'^campaign_archive.js/$', "campaign_archive_js", name='campaign_archive_js'),
)

if settings.DEBUG:
    urlpatterns += patterns(
        "regluit.frontend.views",
        url(r"^goodreads/$", login_required(GoodreadsDisplayView.as_view()), name="goodreads_display"),
        url(r"^goodreads/clear_wishlist/$","clear_wishlist", name="clear_wishlist"),
        url(r"^donate/$", DonateView.as_view(), name="donate"),
        url(r"^celery/clear/$","clear_celery_tasks", name="clear_celery_tasks"),
)