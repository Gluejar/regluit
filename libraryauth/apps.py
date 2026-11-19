from django.apps import AppConfig


class LibraryAuthConfig(AppConfig):
    name = 'regluit.libraryauth'

    def ready(self):
        # Connect the user_activated receiver in signals.py.
        # MUST live in apps.py: Django 4.1 removed `default_app_config`, so an
        # AppConfig defined only in __init__.py is never discovered and ready()
        # never runs. (That regression silently disabled this app's signals from
        # the 2026-06-17 Django 4.2 cutover until this fix.)
        from . import signals  # noqa: F401
