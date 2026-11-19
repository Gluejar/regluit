"""Server-side HTML sanitization for user-entered rich text.

The rich-text fields (``Campaign.description`` / ``Campaign.details`` /
``Work.description`` / edition descriptions) are authored via CKEditor and then
rendered on public pages. CKEditor's own content filtering runs only in the
browser and can be bypassed by POSTing crafted HTML directly, so it is not a
security boundary. We sanitize server-side at render time with ``nh3`` (a
maintained Rust/ammonia binding; ``bleach`` is deprecated).

The allow-list mirrors what the CKEditor toolbar can legitimately produce
(bold/italic, lists, blockquote, links, images, horizontal rules), plus common
tags that can arrive via paste. Everything else -- ``<script>``, ``<style>``,
event handlers, ``javascript:`` URLs, etc. -- is stripped.

See EbookFoundation/security-private#26.
"""
import nh3

ALLOWED_TAGS = {
    'a', 'abbr', 'b', 'blockquote', 'br', 'cite', 'code', 'del', 'em', 'hr',
    'i', 'img', 'ins', 'li', 'ol', 'p', 'pre', 'q', 's', 'small', 'span',
    'strong', 'sub', 'sup', 'u', 'ul',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'table', 'thead', 'tbody', 'tr', 'td', 'th',
}

ALLOWED_ATTRIBUTES = {
    # 'rel' is managed by nh3 via link_rel below (ammonia forbids setting both)
    'a': {'href', 'title', 'target'},
    'img': {'src', 'alt', 'title', 'width', 'height'},
    'td': {'colspan', 'rowspan'},
    'th': {'colspan', 'rowspan', 'scope'},
}

ALLOWED_URL_SCHEMES = {'http', 'https', 'mailto', 'ftp'}


def sanitize_html(value):
    """Return ``value`` with unsafe HTML removed.

    Returns the input unchanged when it is falsy (``None`` / empty string) so it
    is safe to call on nullable model fields.
    """
    if not value:
        return value
    return nh3.clean(
        value,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        url_schemes=ALLOWED_URL_SCHEMES,
        link_rel='noopener noreferrer nofollow',
    )
