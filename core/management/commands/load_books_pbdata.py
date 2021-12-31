import json
from datetime import datetime

from django.core.management.base import BaseCommand

from regluit.core.loaders import add_by_metadata
from regluit.core.loaders.pressbooks import PressbooksScraper

class Command(BaseCommand):
    help = "load books from a json file from pressbooks"
    def add_arguments(self, parser):
        parser.add_argument('filename', help="filename")    
        parser.add_argument(
            '--from',
            action='store',
            dest='from_date',
            default='1-1-2000',
            help='only read records after <from>',
        )

    def handle(self, filename, **options):
        with open(filename, 'r') as jsonfile:
            pb_metadata = json.load(jsonfile)
        self.stdout.write(f'reading {len(pb_metadata)} records')
        try:
            from_date = datetime.strptime(options['from_date'], '%m-%d-%Y')
        except ValueError:
            from_date = datetime.strptime('1-1-2000', '%m-%d-%Y')
        for record in pb_metadata:
            if 'updated' in record:
                updated = datetime.strptime(record['updated'], '%m-%d-%Y')
            if updated < from_date:
                continue
            scraper = PressbooksScraper(record['url'], initial=record)
            add_by_metadata(scraper.metadata)

        self.stdout.write("finished loading")
