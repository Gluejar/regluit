import unicodedata

from django.template.base import Library
from .. import models

register = Library()

@register.filter()
def libname(value):
    """
    returns library name  .
    """
    try:
        vl = long( value )
        lib = models.Library.objects.get(pk=vl)
        return lib.__unicode__()
    except models.Library.DoesNotExist:
        return value

