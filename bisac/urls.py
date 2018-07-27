from django.conf.urls import url, include
from .views import tree

urlpatterns = [
    url(r"^tree$", tree),
]
