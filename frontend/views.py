from django.template import RequestContext
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response, get_object_or_404

from regluit.core import models, bookloader
from regluit.core.search import gluejar_search

def home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('supporter',
            args=[request.user.username]))
    return render(request, 'home.html')

def supporter(request, supporter_username):
    supporter = get_object_or_404(User, username=supporter_username)
    wishlist = supporter.wishlist
    context = {
        "supporter": supporter,
        "wishlist": wishlist,
    }
    return render(request, 'supporter.html', context)

def search(request):
    q = request.GET.get('q', None)
    results = gluejar_search(q)

    # flag search result as on wishlist
    # TODO: make this better and faster
    if request.user:
        for result in results:
            if not result.has_key('isbn_10'):
                continue
            work = models.Work.get_by_isbn(result['isbn_10'])
            if work and work in request.user.wishlist.works.all():
                result['on_wishlist'] = True
            else:
                result['on_wishlist'] = False

    context = {
        "q": q,
        "results": results,
    }
    return render(request, 'search.html', context)

@csrf_exempt
@require_POST
@login_required
def wishlist(request):
    isbn = request.POST.get('isbn', None)
    edition = models.Edition.get_by_isbn(isbn)
    if not edition:
        print "loading book"
        edition = bookloader.add_book(isbn)
    if edition:
        print "adding edition"
        request.user.wishlist.works.add(edition.work)
    # TODO: redirect to work page, when it exists
    return HttpResponseRedirect('/')
