from tastypie.models import ApiKey

import json
import logging

from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.urls import reverse
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View, TemplateView
from django.http import (
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseBadRequest,
    HttpResponseRedirect,
    Http404,
)



import regluit.core.isbn
from regluit.core.bookloader import load_from_yaml
from regluit.api import opds, onix, opds_json
from regluit.api.models import repo_allowed

from regluit.core import models

logger = logging.getLogger(__name__)


def editions(request):
    editions = models.Edition.objects.all()
    return render(request, 'editions.html', 
        {'editions':editions},
    )    

def negotiate_content(request,work_id):
    if request.META.get('HTTP_ACCEPT', None):
        if "opds-catalog" in request.META['HTTP_ACCEPT']:
            return HttpResponseRedirect(reverse('opds_acqusition',args=['all'])+'?work='+work_id)
        elif "text/xml" in request.META['HTTP_ACCEPT']:
            return HttpResponseRedirect(reverse('onix',args=['all'])+'?work='+work_id)
    
    return HttpResponseRedirect(reverse('work', kwargs={'work_id': work_id}))

def featured_work():
    try:
        work = models.Work.objects.filter(featured__isnull=False).distinct().order_by('-featured')[0]
    except:
        #shouldn't occur except in tests
        work = models.Work.objects.all()[0]
    return work

def widget(request, isbn):
    """
    supply info for book panel. parameter is named isbn for historical reasons. can be isbn or work_id
    """
   
    if isbn == 'featured':
        work = featured_work()
    else :    
        if len(isbn)==10:
            isbn = regluit.core.isbn.convert_10_to_13(isbn)
        if len(isbn)==13:
            try:
                identifier = models.Identifier.objects.get(type = 'isbn', value = isbn )
                work = identifier.work
            except models.Identifier.DoesNotExist:
                return render(request, 'widget.html', 
                     { 'work':None,}, 
                    )
        else:
            work= models.safe_get_work(isbn)
    return render(request, 'widget.html', 
         {'work':work, }, 
     )

def featured_cover(request):
    work = featured_work()
    tn = work.cover_image_thumbnail()
    return HttpResponseRedirect(tn if tn else "/static/images/generic_cover_larger.png")

def featured_url(request):
    work = featured_work()
    return HttpResponseRedirect(reverse('work', kwargs={'work_id': work.id}))

def load_yaml(request):
    if request.method == "GET":
        return render(request, 'load_yaml.html', { })
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
    
@csrf_exempt    
def travisci_webhook(request):
    """
    Respond to travis-ci webhooks from Project GITenberg repositories.  If the webhook is successfully parsed,
    the metdata.yaml for the repository is loaded using load_from_yaml.
    https://docs.travis-ci.com/user/notifications/#Webhook-notification
    
    """

    if request.method == "POST":
    
        try:
            
            data = json.loads(request.POST.get('payload'))

            # example of URL to feed to yaml loader:
            # https://github.com/GITenberg/Adventures-of-Huckleberry-Finn_76/raw/master/metadata.yaml
            
            if data['status_message'] == 'Passed' and data['type'] == 'push':
                                       
                # another way to get owner_name / name would be request.META.get('HTTP_TRAVIS_REPO_SLUG', '')
                repo_url = "https://github.com/{}/{}/raw/master/metadata.yaml".format(data['repository']['owner_name'],
                                                                                      data['repository']['name'])
                
                work_id = load_from_yaml(repo_url)
                return HttpResponse('Successful. work_id: {}'.format(work_id))
        
        except Exception as e:
                return HttpResponseBadRequest('Unsuccessful. Exception: {}'.format(unicode(e)))
                
        else:
            
            return HttpResponse('No action')
            
    else:
        return HttpResponse('No action')
        
    
        
class ApiHelpView(TemplateView):
    template_name = "api_help.html"
    def get_context_data(self, **kwargs):
        context = super(ApiHelpView, self).get_context_data(**kwargs)
        
        # base_url passed in to allow us to write absolute URLs for this site
        base_url = self.request.build_absolute_uri("/")[:-1]
        context["base_url"] = base_url
        
        # if user is logged in, pass in the user's API key
        u = auth.get_user(self.request)
        if u.is_authenticated:
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
    json=False
    # https://stackoverflow.com/a/6867976: secret to how to change content-type
    
    def render_to_response(self, context, **response_kwargs):
        if json:
            response_kwargs['content_type'] = "application/vnd.opds.navigation+json"
        else:
            response_kwargs['content_type'] = "application/atom+xml;profile=opds-catalog;kind=navigation"
        return super(TemplateView, self).render_to_response(context, **response_kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(OPDSNavigationView, self).get_context_data(**kwargs)
        if json:
            context["feeds"] = opds_json.feeds()
            context["feed"] = opds_json.get_facet_facet('all')
        else:
            context["feeds"] = opds.feeds()
            context["feed"] = opds.get_facet_facet('all')
        return context

class OPDSAcquisitionView(View):
    json = False
    def get(self, request, *args, **kwargs):
        work = request.GET.get('work', None)
        if work:
            if self.json:
                return HttpResponse(opds_json.opds_feed_for_work(work),
                        content_type="application/opds-publication+json")
            else:
                return HttpResponse(opds.opds_feed_for_work(work),
                        content_type="application/atom+xml;profile=opds-catalog;kind=acquisition")
        facet = kwargs.get('facet')
        page = request.GET.get('page', None)
        order_by =  request.GET.get('order_by', 'newest')
        try:
            page = int(page)
        except:
            page = None
        if self.json:
            facet_class = opds_json.get_facet_class(facet)()
            return HttpResponse(facet_class.feed(page,order_by),
                        content_type="application/opds+json")
        else:
            facet_class = opds.get_facet_class(facet)()
            return HttpResponse(facet_class.feed(page,order_by),
                        content_type="application/atom+xml;profile=opds-catalog;kind=acquisition")


class OnixView(View):

    def get(self, request, *args, **kwargs):
        work = request.GET.get('work', None)
        if work:
            try:
                work=models.safe_get_work(work)
            except models.Work.DoesNotExist:
                raise Http404 
            return HttpResponse(onix.onix_feed_for_work(work),
                            content_type="text/xml")
        facet = kwargs.get('facet', 'all')
        if facet:
            max = request.GET.get('max', 100)
            try:
                max = int(max)
            except:
                max = None
            facet_class = opds.get_facet_class(facet)()
            return HttpResponse(onix.onix_feed(facet_class, max),
                                content_type="text/xml")

