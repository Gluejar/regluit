from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage

from regluit.marc.models import MARCRecord
from regluit.core.models import MARCRecord as OldRecord

class Command(BaseCommand):
    help = "migrate records from files"
    args = ""
    
    def handle(self,  **options):
        editions=[]
        for old_record in OldRecord.objects.all().order_by('-id'):
            if old_record.edition.pk not in editions:
                new_record, created = MARCRecord.objects.get_or_create(id=old_record.pk)
                try:
                    xml_file = default_storage.open(old_record.xml_record)
                    xml_data = xml_file.read()
                    new_record.guts = xml_data
                    new_record.edition = old_record.edition
                    editions.append(old_record.edition.pk)
                    xml_file.close()
                    new_record.save()
                    print 'record %s updated' % new_record.id
                except IOError:
                    if created:
                        new_record.delete()
                    print 'failed opening %s' % old_record.xml_record
