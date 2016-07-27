# vim: set fileencoding=utf-8

from django.conf.urls.defaults import *
from . import views 

urlpatterns = [
    url(r'^q/(?P<runcode>[^/]+)/(?P<qs>\d+)/$',
        views.questionnaire, name='questionset'),
    url(r'^q/([^/]+)/',
        views.questionnaire, name='questionset'),
    url(r'^q/manage/csv/(\d+)/',
        'views.export_csv),
    url(r'^q/manage/sendemail/(\d+)/$',
        views.send_email),
    url(r'^q/manage/manage/sendemails/$',
        views.send_emails),
]
