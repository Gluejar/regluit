from collections import defaultdict
from django.core.management.base import BaseCommand
from regluit.core.models import Ebook

def delete_newest_ebooks(ebooks):
     """
     given a list of ebooks (presumably with the same URL), delete all but the ebook that was created first
     """
     for ebook in sorted(ebooks, key=lambda ebook: ebook.created)[1:]:
         self.stdout.write("deleting ebook.id {}, edition.id {} work.id {}".format(ebook.id,
                                                                       ebook.edition_id,
                                                                       ebook.edition.work_id))
         ebook.delete()
         
         intact = ebooks[0]
         print "leaving undeleted: ebook.id {}, edition.id {} work.id {}".format(
            intact.id,
            intact.edition_id,
            intact.edition.work_id
         )
            

class Command(BaseCommand):
    help = "delete redundant ebooks based on having the same URL"
    
    def handle(self, **options):
        ebooks_by_url = defaultdict(list)
        
        # aggregate ebooks by url
        # consider only active ebooks in deduping 
        for ebook in Ebook.objects.filter(active=True):
            ebooks_by_url[ebook.url].append(ebook)
            
        # look through the URLs locating ones with more than one ebook
        for (url, ebooks) in ebooks_by_url.items():
            if len(ebooks) > 1:
                self.stdout.write(url, len(ebooks))
                delete_newest_ebooks(ebooks)