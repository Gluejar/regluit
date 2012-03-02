from django.conf import settings
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.test.utils import setup_test_environment

from regluit.core import models

from unittest import TestResult

import logging
logger = logging.getLogger(__name__)

def testExperimental(request):
    number_of_works = models.Work.objects.count()
    return HttpResponse("Number of works {0}".format(number_of_works))

    
    
    