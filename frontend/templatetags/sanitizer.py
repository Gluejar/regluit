"""Template filter that renders user rich-text HTML safely.

Use ``{{ value|sanitize }}`` in place of ``{{ value|safe }}`` for any
user-authored rich text (CKEditor output). It strips dangerous markup
server-side (see ``regluit.utils.html.sanitize_html``) and marks the result
safe so the surviving, allow-listed HTML still renders.
"""
from django import template
from django.utils.safestring import mark_safe

from regluit.utils.html import sanitize_html

register = template.Library()


@register.filter(name='sanitize', is_safe=True)
def sanitize(value):
    return mark_safe(sanitize_html(value or ''))
