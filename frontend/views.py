from django.template import RequestContext
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404

from regluit.core import models

def home(request):
    # if the user is logged in send them to their supporter page
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('supporter',
            args=[request.user.username]))
    return render_to_response('home.html', 
        {},
        context_instance=RequestContext(request)
    )

def supporter(request, supporter_username):
    supporter = get_object_or_404(User, username=supporter_username)
    campaigns = models.Campaign.objects.all()
    return render_to_response('supporter.html',
        {"supporter": supporter, "campaigns": campaigns},
        context_instance=RequestContext(request)
    )

def textpage(request, page):	
    return render_to_response(page + '.html', 
        {},
        context_instance=RequestContext(request)
    )
