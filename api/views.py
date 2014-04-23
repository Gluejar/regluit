from tastypie.models import ApiKey

from django.contrib import auth
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic.base import TemplateView

import regluit.core.isbn

from regluit.core import models

def isbn(request,isbn):
    if len(isbn)==10:
        isbn=regluit.core.isbn.convert_10_to_13(isbn)
    try:
        edition = models.Identifier.objects.get( Q(type = 'isbn', value = isbn)).edition
        editions = [edition]
    except models.Identifier.DoesNotExist:
        editions = []
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
    supply info for book panel 
    """
   
        
    if len(isbn)==10:
        isbn = regluit.core.isbn.convert_10_to_13(isbn)
    try:
        identifier = models.Identifier.objects.get( Q( type = 'isbn', value = isbn ))
        work = identifier.work
        edition = identifier.edition
    except models.Identifier.DoesNotExist:
        return render_to_response('widget.html', 
             {'isbn':isbn,'edition':None, 'work':None, 'campaign':None,}, 
             context_instance=RequestContext(request)
            )
    return render_to_response('widget.html', 
         {'isbn':isbn,'edition':edition, 'work':work, 'campaign':work.last_campaign(), }, 
         context_instance=RequestContext(request)
     )

class ApiHelpView(TemplateView):
    template_name = "api_help.html"
    def get_context_data(self, **kwargs):
        context = super(ApiHelpView, self).get_context_data(**kwargs)
        
        # base_url passed in to allow us to write absolute URLs for this site
        base_url = self.request.build_absolute_uri("/")[:-1]
        context["base_url"] = base_url
        
        # if user is logged in, pass in the user's API key
        u = auth.get_user(self.request)
        if u.is_authenticated():
            api_key = ApiKey.objects.filter(user=u)[0].key
            context['api_key'] = api_key
        
        # pass in a sample Campaign whose widget can be displayed
        campaigns = models.Campaign.objects.all()
        if len(campaigns):
            c = campaigns[0]
            isbn = c.work.first_isbn_13
            context["campaign"] = campaigns[0]
            context["campaign_isbn"] = isbn

        return context    
