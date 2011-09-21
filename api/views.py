from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib import auth
from django.contrib.auth.models import User, AnonymousUser
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

def widget(request,isbn):
    """
    Aim is to ultimately supply the following info:
- campaign name
- campaign description
- rights holder
- work title
- work author
- a link to an edition cover
- a link to the campaign on unglue.it- the status, or progress of the ungluing
- when the campaign is finished
- whether the logged in user is a supporter
- whether the logged in user is currently supporting the campaign
    Current implementation is to supply info for current book panel design
    """
   
    # presumably 0 or 1 Edition will match
    editions = models.Edition.objects.filter(Q(isbn_10 = isbn) | Q(isbn_13 = isbn))
    # if 1 edition: should be 0 or 1 corresponding Work
    # for 1 Work, there will be a Campaign or not
    assert len(editions) < 2
   
    if len(editions):
         edition = editions[0]
         try:
             work = edition.work
             campaigns = work.campaigns.all()
         except Exception, e:
             work = None
             campaigns = []
    else:
         edition = None
         work = None
         campaigns = []
         
    u = auth.get_user(request)
    if isinstance(u, User):
        logged_in_username = u.username
    else:
        logged_in_username = None
             
    return render_to_response('widget.html', 
         {'isbn':isbn,'edition':edition, 'work':work, 'campaigns':campaigns, 'logged_in_username':logged_in_username}, 
         context_instance=RequestContext(request)
     )
    