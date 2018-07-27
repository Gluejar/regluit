from django.template import Library
from .. import models

register = Library()

@register.filter()
def libname(value):
    """
    returns library name  .
    """
    try:
        vl = long(value)
        lib = models.Library.objects.get(pk=vl)
        return lib.__unicode__()
    except models.Library.DoesNotExist:
        return value

@register.simple_tag(takes_context=True)
def librarylist(context):
    libraries_to_show = context.get('libraries_to_show', 'approved')
    if libraries_to_show == 'approved':
        context['libraries'] = models.Library.objects.filter(approved=True).order_by('name')
    elif libraries_to_show == 'new':
        context['libraries'] = models.Library.objects.filter(approved=False).order_by('name')
    else:
        context['libraries'] = models.Library.objects.order_by('name')
    return ''
