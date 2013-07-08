# code modified from http://stackoverflow.com/questions/4734645/is-there-a-tool-to-check-database-integrity-in-django/4736176#4736176

from optparse import make_option

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import (
    BaseCommand,
    CommandError,
    NoArgsCommand
)
from django.db import models

def model_name(model):
    return '%s.%s' % (model._meta.app_label, model._meta.object_name)

class Command(BaseCommand):
    args = '[-e|--exclude app_name.ModelName]'
    help = 'Checks constraints in the database and reports violations on stdout'

    option_list = NoArgsCommand.option_list + (
        make_option('-e', '--exclude', action='append', type='string', dest='exclude'),
    )

    def handle(self, *args, **options):
        # TODO once we're on Django 1.2, write to self.stdout and self.stderr instead of plain print

        exclude = options.get('exclude', None) or []

        failed_instance_count = 0
        failed_model_count = 0
        for app in models.get_apps():
            for model in models.get_models(app):
                if model_name(model) in exclude:
                    print 'Skipping model %s' % model_name(model)
                    continue
                fail_count = self.check_model(app, model)
                if fail_count > 0:
                    failed_model_count += 1
                    failed_instance_count += fail_count
        print 'Detected %d errors in %d models' % (failed_instance_count, failed_model_count)

    def check_model(self, app, model):
        meta = model._meta
        if meta.proxy:
            print 'WARNING: proxy models not currently supported; ignored'
            return

        # Define all the checks we can do; they return True if they are ok,
        # False if not (and print a message to stdout)
        def check_foreign_key(model, field):
            foreign_model = field.related.parent_model
            def check_instance(instance):
                try:
                    # name: name of the attribute containing the model instance (e.g. 'user')
                    # attname: name of the attribute containing the id (e.g. 'user_id')
                    getattr(instance, field.name)
                    return True
                except ObjectDoesNotExist:
                    print '%s with pk %s refers via field %s to nonexistent %s with pk %s' % \
                        (model_name(model), str(instance.pk), field.name, model_name(foreign_model), getattr(instance, field.attname))
            return check_instance

        # Make a list of checks to run on each model instance
        checks = []
        for field in meta.local_fields + meta.local_many_to_many + meta.virtual_fields:
            if isinstance(field, models.ForeignKey):
                checks.append(check_foreign_key(model, field))

        # Run all checks
        fail_count = 0
        if checks:
            for instance in model.objects.all():
                print 'Checking model %s ...' % model_name(model)
                for check in checks:
                    if not check(instance):
                        fail_count += 1
        return fail_count