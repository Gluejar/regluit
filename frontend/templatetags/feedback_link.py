"""
Emit the site-wide "feedback" link, with a self-reference guard.

On every page except /feedback/ itself the link carries a ?page=<current-url>
parameter so the feedback form can record where the user came from. On the
feedback page we deliberately drop that parameter: a feedback link that points
back to the feedback page (with the feedback page's own URL encoded into it)
creates an infinite, self-referencing URL space -- each level re-encodes the
one before (%2F -> %252F -> %25252F). Crawler fleets walked that space at tens
of thousands of requests per hour on 2026-07-10 and saturated the web workers
(see INCIDENT_2026-07-10_crawler_trap_flood.md).

Any existing page= parameter is also stripped from the recorded URL, so other
query strings can't reintroduce a level of nesting.
"""
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit

from django import template
from django.urls import reverse

register = template.Library()


def _on_feedback_page(request):
    match = getattr(request, 'resolver_match', None)
    if match is not None and match.url_name == 'feedback':
        return True
    return request.path == reverse('feedback')


def _strip_page_param(url):
    parts = urlsplit(url)
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if k != 'page']
    return urlunsplit(parts._replace(query=urlencode(query)))


@register.simple_tag(takes_context=True)
def feedback_url(context):
    feedback = reverse('feedback')
    request = context.get('request')
    if request is None or _on_feedback_page(request):
        return feedback
    page = _strip_page_param(request.build_absolute_uri())
    return '%s?page=%s' % (feedback, quote(page, safe=''))
