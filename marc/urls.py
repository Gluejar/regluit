from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from . import views 


urlpatterns = patterns(
    "regluit.marc.views",
    url(r"^marc/concatenate/$", "marc_records", name="marc_concatenate"),
    url(r"^marc/all/$", "all_marc_records", name="marc_all"),
    url(r"^marc/upload/$", login_required(views.MARCUpload.as_view()), name="upload_marc"),
)