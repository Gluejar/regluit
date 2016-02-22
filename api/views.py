from tastypie.models import ApiKey

import json
import logging

from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View, TemplateView
from django.http import (
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseRedirect,
    Http404,
)



import regluit.core.isbn
from regluit.core.bookloader import load_from_yaml
from regluit.api import opds, onix
from regluit.api.models import repo_allowed

from regluit.core import models

logger = logging.getLogger(__name__)


def editions(request):
    editions = models.Edition.objects.all()
    return render_to_response('editions.html', 
        {'editions':editions},
        context_instance=RequestContext(request)
    )    

def negotiate_content(request,work_id):
    if request.META.get('HTTP_ACCEPT', None):
        if "opds-catalog" in request.META['HTTP_ACCEPT']:
            return HttpResponseRedirect(reverse('opds_acqusition',args=['all'])+'?work='+work_id)
        elif "text/xml" in request.META['HTTP_ACCEPT']:
            return HttpResponseRedirect(reverse('onix',args=['all'])+'?work='+work_id)
    
    return HttpResponseRedirect(reverse('work', kwargs={'work_id': work_id}))

def widget(request,isbn):
    """
    supply info for book panel. parameter is named isbn for historical reasons. can be isbn or work_id
    """
   
        
    if len(isbn)==10:
        isbn = regluit.core.isbn.convert_10_to_13(isbn)
    if len(isbn)==13:
        try:
            identifier = models.Identifier.objects.get(type = 'isbn', value = isbn )
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
    
@csrf_exempt    
def travisci_webhook(request):
    """
    Respond to travis-ci webhooks from Project GITenberg repositories.  If the webhook is successfully parsed,
    the metdata.yaml for the repository is loaded using load_from_yaml.
    
    """

    if request.method == "POST":
    
        #repo_header = request.META.get('HTTP_TRAVIS_REPO_SLUG', '')
        
        data = json.loads(request.POST.get('payload'))
        
        # [python - How can I get all the request headers in Django? - Stack Overflow](https://stackoverflow.com/questions/3889769/how-can-i-get-all-the-request-headers-in-django)
        import re
        regex = re.compile('^HTTP_')
        all_headers = dict((regex.sub('', header), value) for (header, value) 
              in request.META.items() if header.startswith('HTTP_'))

        # what's the URL to feed to load
        # https://github.com/GITenberg/Adventures-of-Huckleberry-Finn_76/raw/master/metadata.yaml 
        
        if data['status_message'] == 'Passed' and data['type'] == 'push':
                       
            logger.info("data.keys():{}".format(data.keys()))
            logger.info("data['repository']: {}".format(data['repository']))
            repo_url = "https://github.com/{}/{}/raw/master/metadata.yaml".format(data['repository']['owner_name'],
                                                                                  data['repository']['name'])
            try:
                work_id = load_from_yaml(repo_url)
                logger.info("work_id: {}".format(work_id))
                return HttpResponse('successful: {}'.format(work_id))
            except Exception as e:
                logger.info("exception: {}".format(unicode(e)))
                return HttpResponse('unsuccessful: {}'.format(unicode(e)))
                
        else:
            
            return HttpResponse('travisci webhook POST owner_name:{} repo_name: {} type:{} state:{} result:{} status_message:{} commit:{} '.format(
                    data['repository']['owner_name'],
                    data['repository']['name'],
                    data.get('repository', {}).get('name'),
                    data.get('type'),
                    data['state'],
                    data['result'],
                    data.get('status_message'),
                    data.get('commit')
            ))
        
    
        
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
        work = request.GET.get('work', None)
        if work:
            return HttpResponse(opds.opds_feed_for_work(work),
                            content_type="application/atom+xml;profile=opds-catalog;kind=acquisition")
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

