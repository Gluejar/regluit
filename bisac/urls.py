from django.conf.urls import patterns, url, include
from .views import tree

urlpatterns = [
    url(r"^tree$", tree),
]
