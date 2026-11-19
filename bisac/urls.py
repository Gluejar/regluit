from django.urls import re_path as url
from .views import tree

urlpatterns = [
    url(r"^tree$", tree),
]
