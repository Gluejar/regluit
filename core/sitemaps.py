from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse
from regluit.core.models import Work, Edition

class WorkSitemap(Sitemap):
    protocol = 'https'

    def items(self):
        return Work.objects.all()
        
    def priority(self,work):
        if work.last_campaign():
            return '1.0'
        if work.num_wishes>1000:
            return '0.8'
        if work.num_wishes>100:
            return '0.6'
        if work.num_wishes>10:
            return '0.4'
        if work.num_wishes>1:
            return '0.3'
        if work.num_wishes==1:
            return '0.2'
        if work.num_wishes==0:
            return '0.1'
        return '0.1'

class PublisherSitemap(Sitemap):
    priority = 0.2
    protocol = 'https'
            
    def items(self):
        return Edition.objects.exclude(publisher__isnull=True).exclude(publisher="").order_by('publisher').values('publisher').distinct()
    
    def location(self, pub):
        return reverse("bypub_list",args=[pub['publisher']])
