from django import template
from .. import models 
register = template.Library()

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
