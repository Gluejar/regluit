from os.path import join
from datetime import date

from celery.task import task

from django.conf import settings 
from django.template.loader import get_template, render_to_string

from .views import InfoPageView

@task
def save_info_page():
    page_view = InfoPageView()
    page = render_to_string(page_view.template_name, context=page_view.get_context_data())
    today = date.today().isoformat()
    with open(join(settings.PROJECT_DIR, 'logs', 'metrics-%s.html' % today), 'w') as todays_metrics:
        todays_metrics.write(page)
