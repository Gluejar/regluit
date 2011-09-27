from django.conf.urls.defaults import *

urlpatterns = patterns(
    "regluit.payment.views",
    url(r"^testpledge", "testPledge"),
    url(r"^querycampaign", "queryCampaign"),
    url(r"^paypalipn", "paypalIPN")
)
