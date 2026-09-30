"""
Emit the site-wide "feedback" link, and the ?next= value for Sign In / Sign Up.

feedback_url emits a bare /feedback/ on every page. It used to carry a
?page=<current-url> parameter so the feedback form could record where the user
came from, which meant every one of the site's ~2M crawlable pages minted its
own distinct feedback URL. On 2026-09-17 production served 702,435 requests to
/feedback/ spread over 693,968 *distinct* URLs -- a repeat rate of 1.01, so no
cache could absorb it and no block list could keep up with it. That traffic was
a direct cause of four outages totalling 115 minutes (see issue #1261).

The originating page is now recovered in the view from the Referer header (see
frontend.views._originating_page), which needs no URL to carry it.

The earlier, July 2026 problem was different and worse: the feedback link on
/feedback/ itself pointed back at /feedback/ with the feedback page's own URL
encoded into it, so the space was not merely large but *infinite* -- each level
re-encoded the one before (%2F -> %252F -> %25252F). Crawler fleets walked it at
tens of thousands of requests per hour and saturated the web workers (see
INCIDENT_2026-07-10_crawler_trap_flood.md).

Emitting a constant URL makes that recursion structurally impossible, so
feedback_url no longer needs its self-reference guard. auth_next still does:
the Sign In / Sign Up links in base.html embed the current URL as ?next=, and
on the feedback page that would re-grow the chain sideways (feedback ->
superlogin?next=<feedback url> -> feedback?page=<superlogin url> -> ...), so
there auth_next uses the bare request.path instead of the full path.
Everywhere else auth_next passes the browser's URL through exactly -- including
any page= query parameter, which is legitimate pagination state (e.g.
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


@register.simple_tag
def feedback_url():
    """The feedback URL -- the same constant string on every page (#1261)."""
    return reverse('feedback')


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
