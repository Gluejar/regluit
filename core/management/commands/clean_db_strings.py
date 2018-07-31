from django.core.management.base import BaseCommand
from django.db import IntegrityError

from regluit.core import models
from regluit.utils.text import sanitize_line, remove_badxml


class Command(BaseCommand):
    help = "clean work and edition titles, work descriptions, and author and publisher names"
    
    def handle(self, **options):
        work_titles_fixed = edition_titles_fixed = work_descriptions_fixed = author_names_fixed = 0
        publisher_names_fixed = 0
        for work in models.Work.objects.all():
            if sanitize_line(work.title) != work.title:
                work.title = sanitize_line(work.title)
                work.save()
                work_titles_fixed +=1
            if work.description and remove_badxml(work.description) != work.description:
                work.description = remove_badxml(work.description)
                work.save()
                work_descriptions_fixed +=1
        self.stdout.write("work_titles_fixed = {}".format(work_titles_fixed))
        self.stdout.write("work_descriptions_fixed = {}".format(work_descriptions_fixed))
        for edition in models.Edition.objects.all():
            if sanitize_line(edition.title) != edition.title:
                edition.title = sanitize_line(edition.title)
                edition.save()
                edition_titles_fixed +=1
        self.stdout.write("edition_titles_fixed = {}".format(edition_titles_fixed))
        for author in models.Author.objects.all():
            if sanitize_line(author.name) != author.name:
                author.name = sanitize_line(author.name)
                try:
                    author.save()
                except IntegrityError as e:
                    # duplicate entry
                    correct = models.Author.objects.get(name=sanitize_line(author.name))
                    for relator in author.relator_set.all():
                        relator.author = correct
                        relator.save()
                    author.delete() 
                author_names_fixed +=1
        self.stdout.write("author_names_fixed = {}".format(author_names_fixed))
        for publishername in models.PublisherName.objects.all():
            if sanitize_line(publishername.name) != publishername.name:
                publishername.name = sanitize_line(publishername.name)
                try:
                    publishername.save()
                except IntegrityError as e:
                    # duplicate entry
                    correct = models.PublisherName.objects.get(name=sanitize_line(publishername.name))
                    for edition in publishername.editions.all():
                        edition.publisher_name = correct
                        edition.save()
                    for publisher in publishername.key_publisher.all():
                        publisher.name = correct
                        publisher.save()
                    publishername.delete() 
                publisher_names_fixed +=1
        self.stdout.write("publisher_names_fixed = {}".format(publisher_names_fixed))
