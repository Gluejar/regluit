from django.conf.urls import url
from .views import tree

urlpatterns = [
    url(r"^tree$", tree),
]
