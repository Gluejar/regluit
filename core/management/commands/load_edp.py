from django.core.management.base import BaseCommand

from regluit.core.loaders.multiscrape import edp_scrape


class Command(BaseCommand):
    help = "load books from edp-open"
    
    def handle(self, **options):
        edp_scrape()
