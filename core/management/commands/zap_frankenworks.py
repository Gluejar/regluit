"""
Dispose of the Frankenworks and recluster the works.  Print out email addresses of those whose wishlists have been
affected.
"""

from django.core.management.base import BaseCommand
from regluit.test import booktests


class Command(BaseCommand):
    help = "Dispose of the Frankenworks and recluster the works.  Print out email addresses of those whose wishlists have been affected."
    args = "<do>"
    
    def handle(self, do, **options):

        try:
            do = str(do)
            if do.lower() == 'true':
                do = True
            else:
                do = False
        except:
            do = False
            
        print "before..."
        s = booktests.cluster_status()
        print s['results']
        
        booktests.clean_frankenworks(s, do=do)
        s = booktests.cluster_status()
        print "after cleanup...."
        print "results ", s['results']
        print "scattered clusters ", s['scattered_clusters']
        print "franken works", s['franken_works']
