from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Q

from regluit.core import models

def isbn(request,isbn):
    
    editions = models.Edition.objects.filter(Q(isbn_10 = isbn) | Q(isbn_13 = isbn))
    # models.Campaign.objects.filter(work__editions__isbn_13='9780811216999')
    
    return render_to_response('isbn.html', 
        {'isbn':isbn, 'editions':editions},
        context_instance=RequestContext(request)
    )

def editions(request):
    editions = models.Edition.objects.all()
    return render_to_response('editions.html', 
        {'editions':editions},
        context_instance=RequestContext(request)
    )    
