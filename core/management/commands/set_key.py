from django.core.management.base import BaseCommand
from regluit.core.models import Key

class Command(BaseCommand):
    help = "set a core.models.Key with name value"
    args = "<name> <value>"

    def handle(self, name, value, **options):
        (k, created) = Key.objects.get_or_create(name=name)
        k.value = value
        k.save()
        
