from django.template import RequestContext
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response, get_object_or_404

from regluit.core import models, search

def home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('supporter',
            args=[request.user.username]))
    return render(request, 'home.html')

def supporter(request, supporter_username):
    supporter = get_object_or_404(User, username=supporter_username)
    campaigns = models.Campaign.objects.all()
    context = {
        "supporter": supporter,
        "campaigns": campaigns,
    }
    return render(request, 'supporter.html', context)

def search(request):
    q = request.GET.get('q', None)
    results = search.gluejar_search(q)
    context = {
        "q": q,
        "results": results,
    }
    return render(request, 'search.html', context)
