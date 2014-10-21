from django.conf.urls.defaults import *

urlpatterns = patterns(
    "regluit.marc.views",
    url(r"^marc/concatenate/$", "marc_records", name="marc_concatenate"),
    url(r"^marc/all/$", "all_marc_records", name="marc_all"),
)