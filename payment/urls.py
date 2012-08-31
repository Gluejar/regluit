from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns(
    "regluit.payment.views",
    url(r"^handleipn/(?P<module>\w+)$", "handleIPN", name="HandleIPN"),
)


# this should be on only if DEBUG is on

if settings.DEBUG:
    urlpatterns += patterns(
        "regluit.payment.views",
        url(r"^testpledge", "testPledge"),
        url(r"^testauthorize", "testAuthorize"),
        url(r"^testexecute", "testExecute"),
        url(r"^testcancel", "testCancel"),
        url(r"^querycampaign", "queryCampaign"),
        url(r"^checkstatus", "checkStatus"),
        url(r"^testfinish", "testFinish"),
        url(r"^testrefund", "testRefund"),
        url(r"^testmodify", "testModify"),
    )
         
     