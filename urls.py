from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required
from django.contrib.sitemaps.views import index, sitemap
from django.views.decorators.cache import never_cache

from ckeditor_uploader import views as ckedit_views

from regluit.admin import site
from regluit.core.sitemaps import WorkSitemap, PublisherSitemap

sitemaps = {
    'works': WorkSitemap,
    'publishers': PublisherSitemap,
}

urlpatterns = [
    url(r'^api/', include('regluit.api.urls')),
    url(r'', include('regluit.frontend.urls')),
    url(r'', include('regluit.payment.urls')),
    url(r'', include('regluit.libraryauth.urls')),
    url(r'', include('regluit.marc.urls')),
    url(r'^bisac/', include('regluit.bisac.urls')),
    url(r'^selectable/', include('selectable.urls')),
    url(r'^admin/', site.urls),
    url(r'^comments/', include('django_comments.urls')),
    url(r"^notification/", include('notification.urls')),
    url(r'^ckeditor/upload/', login_required(ckedit_views.upload), name='ckeditor_upload'),
    url(
        r'^ckeditor/browse/',
        never_cache(login_required(ckedit_views.browse)),
        name='ckeditor_browse'
    ),
    # questionnaire urls
    url(r'^survey/', include('questionnaire.urls')),
    # sitemaps
    url(r'^sitemap\.xml$', index, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
    url(r'^sitemap-(?P<section>.+)\.xml$', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
]
