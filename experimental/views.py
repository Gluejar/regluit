from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.test.utils import setup_test_environment
from unittest import TestResult

import logging
logger = logging.getLogger(__name__)

def testExperimental(request):
    return HttpResponse("hi there")

    
    
    