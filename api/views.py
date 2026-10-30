import json as json_module
import logging

from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import connection, OperationalError
from django.urls import reverse
from django.shortcuts import render
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View, TemplateView
from django.http import (
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseBadRequest,
    HttpResponseRedirect,
    Http404,
    StreamingHttpResponse,
)



import regluit.core.isbn
from regluit.api import opds, onix, opds_json
from regluit.api.models import repo_allowed
from regluit.core.bookloader import load_from_yaml
from regluit.core.covers import DEFAULT_COVER
from regluit.core import models
from regluit.core.facets import InvalidFacetCombination
from regluit.core.parameters import ORDER_BY_KEYS

logger = logging.getLogger(__name__)

ANONYMOUS_MAX_RECORDS = 100

# OPDS search feeds: per-SELECT time limit, and MySQL's error code when it trips
# ("maximum statement execution time exceeded"). See OPDSAcquisitionView.search_feed.
SEARCH_STATEMENT_LIMIT_MS = 5000
MYSQL_STATEMENT_TIMEOUT = 3024

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
        work = models.Work.objects.first()
    return work

def widget(request, isbn):
    """
    supply info for book panel. parameter is named isbn for historical reasons. can be isbn or work_id
    """

    if isbn == 'featured':
        work = featured_work()
    else :
        if len(isbn)==10:
            # convert_10_to_13 returns None for an invalid ISBN-10; guard the
            # len() below and fall through to the empty-widget response.
            isbn = regluit.core.isbn.convert_10_to_13(isbn)
        if isbn and len(isbn)==13:
            try:
                identifier = models.Identifier.objects.get(type = 'isbn', value = isbn )
                work = identifier.work
            except models.Identifier.DoesNotExist:
                return render(request, 'widget.html',
                     { 'work':None, 'isbn':isbn, },
                    )
        else:
            # isbn may be a work_id, a non-numeric token, or None (invalid
            # ISBN-10). safe_get_work raises Work.DoesNotExist for unknown or
            # non-numeric ids; render an empty widget instead of a 500.
            try:
                work = models.safe_get_work(isbn)
            except models.Work.DoesNotExist:
                return render(request, 'widget.html',
                     { 'work':None, 'isbn':isbn, },
                    )
    return render(request, 'widget.html',
         {'work':work, 'isbn':isbn, },
     )

def featured_cover(request):
    work = featured_work()
    tn = work.cover_image_thumbnail()
    return HttpResponseRedirect(tn if tn else DEFAULT_COVER)

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

            data = json_module.loads(request.POST.get('payload'))

            # example of URL to feed to yaml loader:
            # https://github.com/GITenberg/Adventures-of-Huckleberry-Finn_76/raw/master/metadata.yaml

            if data['status_message'] == 'Passed' and data['type'] == 'push':

                # another way to get owner_name / name would be request.META.get('HTTP_TRAVIS_REPO_SLUG', '')
                repo_url = "https://github.com/{}/{}/raw/master/metadata.yaml".format(data['repository']['owner_name'],
                                                                                      data['repository']['name'])

                work_id = load_from_yaml(repo_url)
                return HttpResponse('Successful. work_id: {}'.format(work_id))

        except Exception as e:
                return HttpResponseBadRequest('Unsuccessful. Exception: {}'.format(str(e)))

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

        # pass in a sample Campaign whose widget can be displayed
        campaigns = models.Campaign.objects.all()
        if len(campaigns):
            c = campaigns[0]
            isbn = c.work.first_isbn_13
            context["campaign"] = campaigns[0]
            context["campaign_isbn"] = isbn

        return context

class OPDSNavigationView(TemplateView):
    json = False
    # https://stackoverflow.com/a/6867976: secret to how to change content-type

    def render_to_response(self, context, **response_kwargs):
        if self.json:
            response_kwargs['content_type'] = "application/vnd.opds.navigation+json"
        else:
            response_kwargs['content_type'] = opds.NAVIGATION
        return super(TemplateView, self).render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super(OPDSNavigationView, self).get_context_data(**kwargs)
        if self.json:
            context["feeds"] = opds_json.feeds()
            context["feed"] = opds_json.get_facet_facet('all')
        else:
            context["feeds"] = opds.feeds()
            context["feed"] = opds.get_facet_facet('all')
        return context

class OPDSAcquisitionView(View):
    json = False
    def get(self, request, *args, **kwargs):
        facet = kwargs.get('facet')
        feed_module = opds_json if self.json else opds
        # Resolve the facet before the ?work= early return, so compound keyword
        # facets 404 on every path (#1095). The instance is reused below rather
        # than rebuilt, since building a facet can query the database.
        facet_class = None
        if facet:
            try:
                facet_class = feed_module.get_facet_class(facet)()
            except InvalidFacetCombination:
                raise Http404("Compound keyword facet URLs are not supported.")
        work = request.GET.get('work', None)
        if work:
            if self.json:
                return StreamingHttpResponse(opds_json.opds_feed_for_work(work),
                        content_type="application/opds-publication+json")
            else:
                return StreamingHttpResponse(opds.opds_feed_for_work(work),
                        content_type=opds.ACQUISITION)
        page = request.GET.get('page', None)
        order_by =  request.GET.get('order_by', 'newest')

        # robots occasionally mangle order_by
        order_by = order_by if order_by in ORDER_BY_KEYS else 'newest'

        try:
            page = int(page)
        except:
            page = None
        if facet_class is None:
            try:
                facet_class = feed_module.get_facet_class(facet)()
            except InvalidFacetCombination:
                raise Http404("Compound keyword facet URLs are not supported.")
        if self.json:
            content_type = "application/opds+json; charset=utf-8"
        else:
            content_type = opds.ACQUISITION
        if opds.has_search_facet(getattr(facet_class, 'facet_object', None)):
            return self.search_feed(request, facet_class, page, order_by, content_type)
        return StreamingHttpResponse(facet_class.feed(page,order_by),
                    content_type=content_type)

    def search_feed(self, request, facet_class, page, order_by, content_type):
        """Serve a search-facet feed (`s.TERM`) under a database time limit.

        A search scans the whole free catalog. On 2026-10-20 a crawler held all
        60 Django threads with 300-420 s searches and took the site down (#1265).
        Here each SELECT gets SEARCH_STATEMENT_LIMIT_MS; one that runs over gets
        a 503 with Retry-After instead of a thread for five minutes.

        The feed is built before responding (it is one page of works) so a
        timeout can still become a clean 503 rather than truncated XML.
        """
        if connection.vendor != 'mysql':
            return HttpResponse(''.join(facet_class.feed(page, order_by)),
                                content_type=content_type)
        with connection.cursor() as cursor:
            cursor.execute("SET SESSION max_execution_time = %s",
                           [SEARCH_STATEMENT_LIMIT_MS])
        if self.json and order_by == 'none':
            # Up to 50,000 works a page: too big to build in memory (#1189), so
            # stream it. The limit stays set until the connection closes at the
            # end of the request (CONN_MAX_AGE is 0), so a slow query still
            # stops; it just truncates the response instead of a 503.
            return StreamingHttpResponse(facet_class.feed(page, order_by),
                                         content_type=content_type)
        try:
            body = ''.join(facet_class.feed(page, order_by))
        except OperationalError as err:
            if not (err.args and err.args[0] == MYSQL_STATEMENT_TIMEOUT):
                raise
            logger.warning("OPDS search feed over %s ms, sent 503: %s",
                           SEARCH_STATEMENT_LIMIT_MS, request.get_full_path())
            response = HttpResponse(
                "This search is taking too long right now. Please try again later.\n",
                status=503, content_type="text/plain; charset=utf-8")
            response['Retry-After'] = '3600'
            # Logged above as a warning. Without this flag Django logs every 5xx
            # as an error, which on this site mails the admins once per request.
            response._has_been_logged = True
            return response
        finally:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SET SESSION max_execution_time = DEFAULT")
            except Exception:
                logger.exception("could not reset max_execution_time")
        return HttpResponse(body, content_type=content_type)

class OnixView(View):
    def get(self, request, *args, **kwargs):
        facet = kwargs.get('facet', 'all')
        # Validate before the ?work= early return (#1095); reused below.
        facet_class = None
        if facet:
            try:
                facet_class = opds.get_facet_class(facet)()
            except InvalidFacetCombination:
                raise Http404("Compound keyword facet URLs are not supported.")
        work = request.GET.get('work', None)

        if work:
            try:
                work = models.safe_get_work(work)
            except models.Work.DoesNotExist:
                raise Http404
            return HttpResponse(onix.onix_feed_for_work(work), content_type="text/xml")

        if not facet:
            return HttpResponseBadRequest(content='No facet provided')

        max_records = request.GET.get('max', ANONYMOUS_MAX_RECORDS)

        try:
            max_records = int(max_records)
        except Exception:
            max_records = ANONYMOUS_MAX_RECORDS
            
        max_records = max_records if request.user.is_authenticated else ANONYMOUS_MAX_RECORDS

        # facet is non-empty here, so facet_class was built and validated above.
        page = request.GET.get('page', None)
        try:
            page = int(page)
        except:
            page = None

        feed = onix.onix_feed(facet_class, max_records, page_number=page)
        return StreamingHttpResponse(feed, content_type="text/xml")

