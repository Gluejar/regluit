from tastypie.api import Api

from django.conf.urls.defaults import *
from django.views.generic.base import TemplateView

from regluit.api import resources
from regluit.api.views import ApiHelpView
from regluit.api.views import OPDSNavigationView, OPDSAcquisitionView


v1_api = Api(api_name='v1')
v1_api.register(resources.UserResource())
v1_api.register(resources.WorkResource())
v1_api.register(resources.IdentifierResource())
v1_api.register(resources.EditionResource())
v1_api.register(resources.CampaignResource())
v1_api.register(resources.AuthorResource())
v1_api.register(resources.SubjectResource())
v1_api.register(resources.WishlistResource())

urlpatterns = patterns('',
    url(r'^help$', ApiHelpView.as_view(), name="api_help"),
    url(r'^widgettest/$',TemplateView.as_view(template_name="widget_embed.html")),
    url(r'^widget/(?P<isbn>\w+)/$','regluit.api.views.widget', name="widget"),
    url(r"^opds/$", OPDSNavigationView.as_view(template_name="opds.xml"), name="opds"),
    url(r"^opds/(?P<facet>[^/]+)/$", OPDSAcquisitionView.as_view(), name="opds_acqusition"),
    (r'^', include(v1_api.urls)),
)
