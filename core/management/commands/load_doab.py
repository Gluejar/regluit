import datetime
from django.core.management.base import BaseCommand

from regluit.core.loaders import doab

def timefromiso(datestring):
    try:
        return datetime.datetime.strptime(datestring, "%Y-%m-%d")
    except:
        return datetime.datetime.strptime(datestring, "%Y-%m-%dT%H:%M:%S")

class Command(BaseCommand):
    help = "load doab books via oai"

    def add_arguments(self, parser):
        parser.add_argument('from_date', nargs='?', type=timefromiso,
                            default=None, help="YYYY-MM-DD to start")
        parser.add_argument('--until', nargs='?', type=timefromiso,
                            default=None, help="YYYY-MM-DD to end")
        parser.add_argument('--max', nargs='?', type=int, default=None, help="max desired records")

    def handle(self, from_date, **options):
        until_date = options['until']
        max = options['max']
        self.stdout.write('starting at date:{} until:{}, max: {}'.format(
                          from_date, until_date, max))
        records, new_doabs, last_time = doab.load_doab_oai(from_date, until_date, limit=max)
        self.stdout.write('loaded {} records ({} new), ending at {}'.format(
            records, new_doabs, last_time))
