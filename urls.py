from django.conf.urls import patterns, url, include
from django.contrib.sitemaps.views import index, sitemap

from frontend.views import social_auth_reset_password
from regluit.admin import site
from regluit.core.sitemaps import WorkSitemap, PublisherSitemap

sitemaps = {
        'works': WorkSitemap,
        'publishers': PublisherSitemap,
    }

urlpatterns = [
    url(r'^socialauth/reset_password/$', social_auth_reset_password, name="social_auth_reset_password"),
    url(r'^api/', include('regluit.api.urls')),
    url(r'', include('regluit.frontend.urls')),
    url(r'', include('regluit.payment.urls')),
    url(r'', include('regluit.libraryauth.urls')),
    url(r'', include('regluit.marc.urls')),
    url(r'^bisac/', include('regluit.bisac.urls')),
    url(r'^selectable/', include('selectable.urls')),
    url(r'^admin/', include(site.urls)), 
    url(r'^comments/', include('django_comments.urls')),
    url(r"^notification/", include('notification.urls')),
    url(r'^ckeditor/', include('ckeditor.urls')),
    # questionnaire urls
    url(r'^survey/', include('regluit.questionnaire.urls')),
    # sitemaps
    url(r'^sitemap\.xml$', index, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
    url(r'^sitemap-(?P<section>.+)\.xml$', sitemap, {'sitemaps': sitemaps}),
]
