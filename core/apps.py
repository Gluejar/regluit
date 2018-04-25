from django.apps import AppConfig
from django.db.models.signals import post_migrate

class CoreConfig(AppConfig):
    name = 'regluit.core'
    verbose_name = ' core objects'

    def ready(self):
        from regluit.core.signals import create_notice_types
        post_migrate.connect(create_notice_types, sender=self)