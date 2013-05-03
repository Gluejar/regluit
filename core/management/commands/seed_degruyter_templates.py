"""
seed empty but initialized deGruyter books with something useful
"""

from django.core.management.base import BaseCommand
from regluit.core.models import Work

class Command(BaseCommand):
    help = "Seed empty but initialized deGruyter books with something useful. Takes filename containing seed description as argument. Can be safely run more than once; will ignore books with descriptions."
    
    def handle(self, filename, **options):
        books = Work.objects.filter(editions__publisher_name__id=4311, campaigns__status="INITIALIZED")
        for book in books:
            if not 'degruyter_countdown' in book.description:
                """
                read in file and prepend to description
                ignores descriptions that already start with the seed file
                """
                seed_file = open(filename)
                book.description = seed_file.read() + book.description
                book.save()
                seed_file.close()