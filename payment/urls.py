from django.conf.urls.defaults import *
from django.conf import settings


urlpatterns = patterns(
    "regluit.payment.views",
    url(r"^paypalipn", "handleIPN", name="HandleIPN"),
    url(r"^amazonipn", "handleIPN", name="HandleIPN"),
)

# Amazon payment URLs
urlpatterns += patterns(
    "regluit.payment.amazon",
     url(r"^amazonpaymentreturn", "amazonPaymentReturn", name="AmazonPaymentReturn"),
)

if not settings.IS_PREVIEW:
    urlpatterns += patterns(
        "regluit.payment.views",
        url(r"^testpledge", "testPledge"),
        url(r"^testauthorize", "testAuthorize"),
        url(r"^testexecute", "testExecute"),
        url(r"^testcancel", "testCancel"),
        url(r"^querycampaign", "queryCampaign"),
        url(r"^runtests", "runTests"),
        url(r"^paymentcomplete","paymentcomplete"),
        url(r"^checkstatus", "checkStatus"),
        url(r"^testfinish", "testFinish"),
        url(r"^testrefund", "testRefund"),
        url(r"^testmodify", "testModify"),
    )
         
     