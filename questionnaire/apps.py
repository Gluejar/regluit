# questionnaire/apps.py
import imp
from django.conf import settings

from . import qprocessors, add_type  # make sure ours are imported first # noqa
from . import __name__ as app_name
from django.apps import AppConfig

class QuestionnaireConfig(AppConfig):
    name = app_name
    verbose_name = "FEF Questionnaire"
    label = 'questionnaire'

    def ready(self):
  
        add_type('sameas', 'Same as Another Question (put sameas=question.number in checks or sameasid=question.id)')

        for app in settings.INSTALLED_APPS:
            try:
                app_path = __import__(app, {}, {}, [app.split('.')[-1]]).__path__
            except AttributeError:
                continue

            try:
                imp.find_module('qprocessors', app_path)
            except ImportError:
                continue

            __import__("%s.qprocessors" % app)
