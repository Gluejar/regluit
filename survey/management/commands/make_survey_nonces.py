import string
from django.core.management.base import BaseCommand
from ...models import Landing


class Command(BaseCommand):
    help = "make survey nonces with the specified label"
    args = "<how_many> <label>"

    
    def handle(self, how_many=1, label="no label yet", **options):
        how_many=int(how_many)
        while how_many>0:
            landing = Landing.objects.create(label=label)
            print landing.nonce
            how_many -= 1
