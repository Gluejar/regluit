# vim: set fileencoding=utf-8

from django.conf.urls import *
from .views import *


urlpatterns = patterns(
    '',
    url(r'^$',
        questionnaire, name='questionnaire_noargs'),
    url(r'^csv/(?P<qid>\d+)/$',
        export_csv, name='export_csv'),
    url(r'^(?P<runcode>[^/]+)/progress/$',
        get_async_progress, name='progress'),
    url(r'^take/(?P<questionnaire_id>[0-9]+)/$', generate_run),
    url(r'^$', 'questionnaire.page.views.page', {'page_to_render' : 'index'}),
    url(r'^(?P<page_to_render>.*)\.html$', 'questionnaire.page.views.page'),
    url(r'^(?P<lang>..)/(?P<page_to_trans>.*)\.html$', 'questionnaire.page.views.langpage'),
    url(r'^setlang/$', 'questionnaire.views.set_language'),
    url(r'^landing/(?P<nonce>\w+)/$', SurveyView.as_view(), name="landing"),
        url(r'^(?P<runcode>[^/]+)/(?P<qs>[-]{0,1}\d+)/$',
            questionnaire, name='questionset'),
    url(r'^q/manage/csv/(\d+)/',
        'questionnaire.views.export_csv', name="export_csv"),
)

if not use_session:
    urlpatterns += patterns(
        '',
        url(r'^(?P<runcode>[^/]+)/$',
            questionnaire, name='questionnaire'),
        url(r'^(?P<runcode>[^/]+)/(?P<qs>[-]{0,1}\d+)/prev/$',
            redirect_to_prev_questionnaire,
            name='redirect_to_prev_questionnaire'),
    )
else:
    urlpatterns += patterns(
        '',
        url(r'^$',
            questionnaire, name='questionnaire'),
        url(r'^prev/$',
            redirect_to_prev_questionnaire,
            name='redirect_to_prev_questionnaire')
    )
