from itertools import islice
from django.core.management.base import BaseCommand
from regluit.core import (mobigen, tasks)


class Command(BaseCommand):
    help = "For campaign works without a mobi ebook, generate mobi ebooks where possible."
    args = "<limit> <async>"
    
    def handle(self, limit=None, async=True, **options):
        
        if limit is not None:
            limit = int(limit)

        for (i, edition) in enumerate(islice(mobigen.editions_to_convert(), limit)):
            
            print (i, edition.work.get_absolute_url())
            
            if async:
                task = tasks.generate_mobi_ebook_for_edition.delay(edition)
                print (task.id)
            else:
                ebook = mobigen.generate_mobi_ebook_for_edition(edition)
                print (ebook.id)
