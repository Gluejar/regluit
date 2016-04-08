from django.conf.urls import patterns, url, include

urlpatterns = patterns("",
    url(r"^tree$", "regluit.bisac.views.tree"),
)
