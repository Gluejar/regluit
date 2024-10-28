from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from regluit.core.models import Work, Edition

class WorkSitemap(Sitemap):
    protocol = 'https'
    limit = 10000

    def items(self):
        return Work.objects.filter(is_free=True)
        
    def priority(self,work):
        return '{:.1f}'.format(work.priority()/5.0)
