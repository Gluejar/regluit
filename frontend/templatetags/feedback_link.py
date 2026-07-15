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

Two tags cooperate to make the URL space finite:

- feedback_url: drops ?page= on the feedback page itself.
- auth_next: the Sign In / Sign Up links in base.html embed the current URL
  as ?next=. On the feedback page that would re-grow the chain sideways
  (feedback -> superlogin?next=<feedback url> -> feedback?page=<superlogin
  url> -> ...), so there auth_next uses the bare request.path instead of the
  full path. Everywhere else both tags pass the browser's URL through exactly
  -- including any page= query parameter, which is legitimate pagination
  state (e.g. /search/?q=...&page=2). With both rules, alternating
  feedback/login crawls reach a fixed point instead of growing.
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


@register.simple_tag(takes_context=True)
def auth_next(context):
    """Urlencoded value for the ?next= parameter on Sign In / Sign Up links.

    Reuses an incoming ?next= verbatim (stable propagation on login and
    registration pages); on the feedback page uses the bare path so the
    feedback/login link chain cannot grow; otherwise the full current path.
    """
    request = context.get('request')
    if request is None:
        return ''
    incoming = request.GET.get('next')
    if incoming:
        return quote(incoming, safe='')
    if _on_feedback_page(request):
        return quote(request.path, safe='')
    return quote(request.get_full_path(), safe='')
