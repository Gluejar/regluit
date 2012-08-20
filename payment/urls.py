from django.conf.urls.defaults import *
from django.conf import settings
from regluit.payment.views import StripeView, BalancedView, WepayView

urlpatterns = patterns(
    "regluit.payment.views",
    url(r"^handleipn/(?P<module>\w+)$", "handleIPN", name="HandleIPN"),
)

# Amazon payment URLs
urlpatterns += patterns(
    "regluit.payment.amazon",
     url(r"^amazonpaymentreturn", "amazonPaymentReturn", name="AmazonPaymentReturn"),
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
        url(r"^runtests", "runTests"),
        url(r"^paymentcomplete","paymentcomplete"),
        url(r"^checkstatus", "checkStatus"),
        url(r"^testfinish", "testFinish"),
        url(r"^testrefund", "testRefund"),
        url(r"^testmodify", "testModify"),
        url(r"^stripe/test", StripeView.as_view()),
        url(r"^balanced/test", BalancedView.as_view()),
        url(r"^wepay/test", WepayView.as_view()),
    )
         
     