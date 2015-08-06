from tastypie.models import ApiKey

from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic.base import View, TemplateView
from django.http import (
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseRedirect,
)

import regluit.core.isbn
from regluit.core.bookloader import load_from_yaml
from regluit.api import opds
from regluit.api.models import repo_allowed

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
    supply info for book panel. parameter is named isbn for historical reasons. can be isbn or work_id
    """
   
        
    if len(isbn)==10:
        isbn = regluit.core.isbn.convert_10_to_13(isbn)
    if len(isbn)==13:
        try:
            identifier = models.Identifier.objects.get( Q( type = 'isbn', value = isbn ))
            work = identifier.work
        except models.Identifier.DoesNotExist:
            return render_to_response('widget.html', 
                 { 'work':None,}, 
                 context_instance=RequestContext(request)
                )
    else:
        work= models.safe_get_work(isbn)
    return render_to_response('widget.html', 
         {'work':work, }, 
         context_instance=RequestContext(request)
     )

def load_yaml(request):
    if request.method == "GET":
        return render_to_response('load_yaml.html', { }, context_instance=RequestContext(request))
    repo_url = request.POST.get('repo_url', None)
    if not repo_url:
        return HttpResponse('needs repo_url')
    (allowed,reason) =repo_allowed(repo_url)
    if not allowed:
        return HttpResponse('repo_url not allowed: '+reason)
    try:
        work_id = load_from_yaml(repo_url)
        return HttpResponseRedirect(reverse('work', args=[work_id]))
    except:    
        return HttpResponse('unsuccessful')
        
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

class OPDSNavigationView(TemplateView):
    
    # http://stackoverflow.com/a/6867976: secret to how to change content-type
    
    def render_to_response(self, context, **response_kwargs):
        response_kwargs['content_type'] = "application/atom+xml;profile=opds-catalog;kind=navigation"
        return super(TemplateView, self).render_to_response(context, **response_kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(OPDSNavigationView, self).get_context_data(**kwargs)
        context["feeds"] = opds.feeds()
        context["feed"] = opds.get_facet_facet('all')
        return context

class OPDSAcquisitionView(View):

    def get(self, request, *args, **kwargs):
        facet = kwargs.get('facet')
        page = request.GET.get('page', None)
        order_by =  request.GET.get('order_by', 'newest')
        try:
            page = int(page)
        except:
            page = None
        facet_class = opds.get_facet_class(facet)()
        return HttpResponse(facet_class.feed(page,order_by),
                            content_type="application/atom+xml;profile=opds-catalog;kind=acquisition")
