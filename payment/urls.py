from django.conf.urls.defaults import *

urlpatterns = patterns(
    "regluit.payment.views",
    url(r"^testpledge", "testPledge"),
    url(r"^testauthorize", "testAuthorize"),
    url(r"^testexecute", "testExecute"),
    url(r"^testcancel", "testCancel"),
    url(r"^querycampaign", "queryCampaign"),
    url(r"^paypalipn", "paypalIPN", name="PayPalIPN"),
    url(r"^runtests", "runTests"),
    url(r"^paymentcomplete","paymentcomplete")
)
