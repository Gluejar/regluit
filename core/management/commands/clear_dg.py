from django.core.management.base import BaseCommand

from regluit.core import models, bookloader

class Command(BaseCommand):
    help = "clear deG descriptions"
    
    def handle(self, **options):
        qs=models.Work.objects.filter(description__icontains='degruyter_countdown')
        for work in qs:
            work.description = ''
            work.save()
