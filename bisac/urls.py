from django.conf.urls.defaults import *

urlpatterns = patterns("",
    url(r"^tree$", "regluit.bisac.views.tree"),
)
