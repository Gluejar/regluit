"""
{{ raw|urldecode }}
"""
from urllib.parse import unquote

from django.template import Library
from django.template.defaultfilters import stringfilter

register = Library()

@register.filter()
@stringfilter
def urldecode(value):
    return unquote(value)

