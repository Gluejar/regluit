from django.apps import AppConfig

default_app_config = 'regluit.libraryauth.LibraryAuthConfig'

class LibraryAuthConfig(AppConfig):
    name = 'regluit.libraryauth'

    def ready(self):
        from . import signals
