import datetime
from django.core.management.base import BaseCommand

from regluit.core.loaders import doab

def timefromiso(datestring):
    return datetime.datetime.strptime(datestring, "%Y-%m-%d")

class Command(BaseCommand):
    help = "load doab books via oai"
    
    def add_arguments(self, parser):
        parser.add_argument('from_date', nargs='?', type=timefromiso,
                            default=None, help="YYYY-MM-DD to start")
        parser.add_argument('--from_id', nargs='?', type=int, default=0, help="id to start with")    
        parser.add_argument('--max', nargs='?', type=int, default=None, help="max desired records")    
    
    def handle(self, **options):
        from_date = options['from_date']
        from_id = options['from_id']
        max = options['max']
        self.stdout.write('starting at date:{}, id: {}, max: {}'.format(from_date, from_id, max))
        records, new_doabs, last_doab = doab.load_doab_oai(from_date, from_id=from_id, limit=max)
        self.stdout.write('loaded {} records ({} new), ending at {}'.format(records, new_doabs, last_doab))
