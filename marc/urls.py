from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required
from . import views 


urlpatterns = [
    url(r"^marc/concatenate/$", views.marc_records, name="marc_concatenate"),
    url(r"^marc/all/$", views.all_marc_records, name="marc_all"),
    url(r"^marc/upload/$", login_required(views.MARCUpload.as_view()), name="upload_marc"),
]