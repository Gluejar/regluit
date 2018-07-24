from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from regluit.core.models import Work, Edition

class WorkSitemap(Sitemap):
    protocol = 'https'
    limit = 10000

    def items(self):
        return Work.objects.all()
        
    def priority(self,work):
        return '{:.1f}'.format(work.priority()/5.0)

class PublisherSitemap(Sitemap):
    priority = 0.2
    protocol = 'https'
            
    def items(self):
        return Edition.objects.exclude(publisher_name__isnull=True).order_by('publisher_name__name').values('publisher_name').distinct()
    
    def location(self, pub):
        return reverse("bypubname_list",args=[pub['publisher_name']])
