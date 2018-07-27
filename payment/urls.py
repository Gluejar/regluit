from django.conf import settings
from django.conf.urls import url, include

from regluit.payment import views

urlpatterns = [
    url(r"^handleipn/(?P<module>\w+)$", views.handleIPN, name="HandleIPN"),
]


# this should be on only if DEBUG is on

if settings.DEBUG:
    urlpatterns += [
        url(r"^testauthorize", views.testAuthorize),
        url(r"^testexecute", views.testExecute),
        url(r"^testcancel", views.testCancel),
        url(r"^querycampaign", views.queryCampaign),
        url(r"^checkstatus", views.checkStatus),
        url(r"^testfinish", views.testFinish),
        url(r"^testrefund", views.testRefund),
        url(r"^testmodify", views.testModify),
        url(r"^stripe/test", views.StripeView.as_view())
    ]
         
     