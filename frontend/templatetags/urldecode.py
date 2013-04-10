"""
{{ raw|urldecode }}
"""
from django.template.defaultfilters import stringfilter
from django.template.base import Library
from urllib import unquote

register = Library()

@register.filter()
@stringfilter
def urldecode(value):
    return unquote(value)
	
