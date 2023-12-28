#!/usr/bin/python
# vim: set fileencoding=utf-8

import logging



from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404

from .models import Landing


def to_model(request, **kwargs):
    nonce = kwargs['nonce']
    landing = get_object_or_404(Landing, nonce=nonce)
    if landing.content_object:
        work_id = str(landing.content_object.id)
        return HttpResponseRedirect(reverse('work', kwargs={'work_id': work_id}))
    else:
        return HttpResponseRedirect('/')

