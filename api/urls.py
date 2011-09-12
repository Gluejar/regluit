from django.conf.urls.defaults import *
from tastypie.api import Api
from regluit.api import models

api = Api()
api.register(models.WorkResource())

urlpatterns = patterns('',
    # The normal jazz here...
    (r'^api/', include(api.urls)),
)
