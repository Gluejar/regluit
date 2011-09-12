from django.template import RequestContext
from django.shortcuts import render_to_response

from regluit.core import models

def home(request):
    campaigns = models.Campaign.objects.all()
    return render_to_response('home.html', 
        {"campaigns": campaigns},
        context_instance=RequestContext(request)
    )

def panel(request):
    return render_to_response('book-panel.html',
        {},
        context_instance=RequestContext(request)
    )
