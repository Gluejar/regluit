from django.conf.urls.defaults import *
from django.conf import settings

# django-merchant integration
from billing import get_integration

amazon_fps_obj = get_integration("fps")
fps_recur_obj = get_integration("fps")

urlpatterns = patterns(
    "regluit.payment.views",
    url(r"^paypalipn", "paypalIPN", name="PayPalIPN"),
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
    urlpatterns += patterns('',
         (r'^fps/', include(amazon_fps_obj.urls)),
         url(r'^testfps/$', 'regluit.payment.views.testfps', name='testfps'),
    )
    
         
     