import notification.urls

from django.conf.urls.defaults import *

from frontend.views import social_auth_reset_password
from regluit.admin import admin_site
from regluit.core.sitemaps import WorkSitemap, PublisherSitemap

sitemaps = {
        'works': WorkSitemap,
        'publishers': PublisherSitemap,
    }

urlpatterns = patterns('',
    url(r'^socialauth/reset_password/$', social_auth_reset_password, name="social_auth_reset_password"),
    url(r'^api/', include('regluit.api.urls')),
    url(r'', include('regluit.frontend.urls')),
    url(r'', include('regluit.payment.urls')),
    url(r'', include('regluit.libraryauth.urls')),
    url(r'^selectable/', include('selectable.urls')),
    url(r'^admin/', include(admin_site.urls)), 
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^notification/', include(notification.urls)),
    url(r'^ckeditor/', include('ckeditor.urls')),
)

urlpatterns += patterns('django.contrib.sitemaps.views',
    (r'^sitemap\.xml$', 'index', {'sitemaps': sitemaps}),
    (r'^sitemap-(?P<section>.+)\.xml$', 'sitemap', {'sitemaps': sitemaps}),
)
