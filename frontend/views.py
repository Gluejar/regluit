from django.template import RequestContext
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404

from regluit.core import models

def home(request):
    return render_to_response('home.html', 
        {},
        context_instance=RequestContext(request)
    )

def user(request, username):
    u = get_object_or_404(User, username=username)
    return render_to_response('user.html',
        {"subscriber": u},
        context_instance=RequestContext(request)
    )
