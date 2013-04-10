from django.conf.urls.defaults import *
from frontend.forms import ProfileForm
from frontend.views import superlogin
from django.views.generic.simple import direct_to_template
from regluit.admin import admin_site
import notification.urls
from regluit.core.sitemaps import WorkSitemap, PublisherSitemap

sitemaps = {
        'works': WorkSitemap,
        'publishers': PublisherSitemap,
    }

urlpatterns = patterns('',
    url(r'^accounts/activate/complete/$',superlogin,
          {'template_name': 'registration/activation_complete.html'}),
    url(r'^accounts/login/pledge/$',superlogin,
          {'template_name': 'registration/from_pledge.html'}),
    url(r'^accounts/login/add/$',superlogin,
          {'template_name': 'registration/from_add.html'}),
    url(r'^accounts/login-error/$',superlogin,
          {'template_name': 'registration/from_error.html'}),
    (r'^accounts/edit/$', 'regluit.frontend.views.edit_user'),
    (r'^accounts/', include('registration.backends.default.urls')),
    url('accounts/', include('email_change.urls')),
    url(r"^accounts/login/welcome/$", direct_to_template, 
        {'template': 'registration/welcome.html',
            'extra_context': {'suppress_search_box': True,} 
        }), 
    url(r"^accounts/superlogin/welcome/$", direct_to_template, 
        {'template': 'registration/welcome.html',
            'extra_context': {'suppress_search_box': True,} 
        }), 
    (r'^socialauth/', include('social_auth.urls')),
    (r'^api/', include('regluit.api.urls')),
    (r'', include('regluit.frontend.urls')),
    (r'', include('regluit.payment.urls')),
    (r'^selectable/', include('selectable.urls')),
    url(r'^admin/', include(admin_site.urls)), 
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^notification/', include(notification.urls)),

    (r'^ckeditor/', include('ckeditor.urls')),
)

urlpatterns += patterns('django.contrib.sitemaps.views',
    (r'^sitemap\.xml$', 'index', {'sitemaps': sitemaps}),
    (r'^sitemap-(?P<section>.+)\.xml$', 'sitemap', {'sitemaps': sitemaps}),
)
