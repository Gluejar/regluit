import csv
import json
import boto3
from botocore.exceptions import ClientError

from django.conf import settings
from django.core.management.base import BaseCommand

from regluit.core.models import Edition, Identifier

s3 = boto3.resource('s3')



class Command(BaseCommand):
    help = "translate doab ids to handles"
    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='?', help="filename")    
        parser.add_argument('--old_id', nargs='?', default=None, help="id to translate")    

    def handle(self, filename, **options):
        self.stdout.write("doab ids to start: %s" % Identifier.objects.filter(type='doab').count())
        with open(filename, 'r') as jsonfile:
            newdoab = json.loads(jsonfile.read())
        done = 0
        if options['old_id']:
            to_do = Identifier.objects.filter(type='doab', value=options['old_id'])
        else:
            to_do = Identifier.objects.filter(type='doab')
        for doab in to_do:
            if doab.value.startswith("20.500.12854"):
                continue
            if doab.value in newdoab:
                # already done
                if Identifier.objects.filter(type='doab', value=newdoab[doab.value]).exists():
                    doab.delete()
                else:
                    old_cover_file_name = 'doab/%s/cover' % doab.value
                    new_cover_file_name = 'doab/%s' % newdoab[doab.value]
                    self.move_cover(old_cover_file_name, new_cover_file_name)
                    doab.value = newdoab[doab.value]
                    doab.save()
            else:
                doab.delete()
            done += 1
        self.stdout.write("doab ids at end: %s" % Identifier.objects.filter(type='doab').count())
        self.stdout.write("done:: %s" % done)

    def move_cover(self, old_name, new_name):
        if old_name == new_name:
            return
        old_url = "https://{}.s3.amazonaws.com{}".format(
            settings.AWS_STORAGE_BUCKET_NAME, old_name)
        new_url = "https://{}.s3.amazonaws.com{}".format(
            settings.AWS_STORAGE_BUCKET_NAME, new_name)
        copy_source = {
            'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'Key': old_name
        }
        try:
            s3.meta.client.copy_object(
                CopySource=copy_source,
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=new_name, ACL='public-read')

            for ed in Edition.objects.filter(cover_image__contains=old_name):
                ed.cover_image = new_url
                ed.save()

            s3.meta.client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=old_name,)
        except ClientError:
            self.stdout.write("problem moving %s to %s" % (old_name, new_name))
