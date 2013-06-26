import pickle

import notification
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Displays currently queues notices from django-notification"
    
    def handle(self, **options):
        for (i, queued_batch) in enumerate(notification.models.NoticeQueueBatch.objects.all()):
            print i, queued_batch.id, pickle.loads(str(queued_batch.pickled_data).decode("base64")) 
