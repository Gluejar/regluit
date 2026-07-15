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

The guard alone terminates the recursive chain: a feedback URL can only be
embedded into a ?page= parameter by a page that is not the feedback page, so
nesting can never exceed one level. On all other pages the recorded URL is
passed through exactly as the browser requested it -- including any page=
query parameter, which is legitimate pagination state there (e.g.
/search/?q=...&page=2).
"""
from urllib.parse import quote

from django import template
from django.urls import reverse

register = template.Library()


def _on_feedback_page(request):
    match = getattr(request, 'resolver_match', None)
    if match is not None and match.url_name == 'feedback':
        return True
    return request.path == reverse('feedback')


@register.simple_tag(takes_context=True)
def feedback_url(context):
    feedback = reverse('feedback')
    request = context.get('request')
    if request is None or _on_feedback_page(request):
        return feedback
    return '%s?page=%s' % (feedback, quote(request.build_absolute_uri(), safe=''))
