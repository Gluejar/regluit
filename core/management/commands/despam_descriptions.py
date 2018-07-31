from django.core.management.base import BaseCommand

from regluit.core import models, bookloader

class Command(BaseCommand):
    help = "check description db for free ebook spam"
    
    def handle(self, **options):
        spam_strings=["1stWorldLibrary.ORG", "GeneralBooksClub.com", "million-books.com", "AkashaPublishing.Com"]
        for spam_string in spam_strings:
            qs=models.Work.objects.filter(description__icontains=spam_string)
            self.stdout.write("Number of Works with %s in description: %s" % (spam_string, qs.count()))
        
            for work in qs:
                work.description = bookloader.despam_description(work.description)
                self.stdout.write("updating work %s" % work )
                bookloader.add_openlibrary(work, hard_refresh = True)           
