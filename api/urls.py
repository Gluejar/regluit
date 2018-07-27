from tastypie.api import Api

from django.conf.urls import url, include
from django.views.generic.base import TemplateView

from regluit.api import resources
from regluit.api.views import ApiHelpView
from regluit.api.views import OPDSNavigationView, OPDSAcquisitionView
from regluit.api.views import OnixView
from regluit.api.views import (
    travisci_webhook, 
    load_yaml, 
    negotiate_content, 
    widget, 
    featured_cover,
    featured_url,
    )


v1_api = Api(api_name='v1')
v1_api.register(resources.WorkResource())
v1_api.register(resources.IdentifierResource())
v1_api.register(resources.EditionResource())
v1_api.register(resources.CampaignResource())
v1_api.register(resources.AuthorResource())
v1_api.register(resources.SubjectResource())
v1_api.register(resources.FreeResource())
v1_api.register(resources.PublisherResource())
v1_api.register(resources.EbookResource())

urlpatterns = [
    url(r'^help$', ApiHelpView.as_view(), name="api_help"),
    url(r'^widget/(?P<isbn>\w+)/$', widget, name="widget"),
    url(r'^featured_cover$', featured_cover, name="featured_cover"),
    url(r'^featured_url$', featured_url, name="featured_url"),
    url(r"^opds/$", OPDSNavigationView.as_view(template_name="opds.xml"), name="opds"),
    url(r"^opdsjson/$", OPDSNavigationView.as_view(template_name="opds.json", json=True), name="opdsjson"),
    url(r"^opds/(?P<facet>.*)/$", OPDSAcquisitionView.as_view(), name="opds_acqusition"),
    url(r"^opdsjson/(?P<facet>.*)/$", OPDSAcquisitionView.as_view(json=True), name="opdsjson_acqusition"),
    url(r"^onix/(?P<facet>.*)/$", OnixView.as_view(), name="onix"),
    url(r"^onix/$", OnixView.as_view(), name="onix_all"),
    url(r'^id/work/(?P<work_id>\w+)/$', negotiate_content, name="work_identifier"),
    url(r'^loader/yaml$', load_yaml, name="load_yaml"),
    url(r'^travisci/webhook$', travisci_webhook, name="travisci_webhook"),
    url(r'^', include(v1_api.urls)),
]
