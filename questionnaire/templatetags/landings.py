import django.template 
from django.template import Template, Context
register = django.template.Library()

@register.simple_tag(takes_context=True)
def render_with_landing(context, text):
    block_context = Context({'landing_object' : context['runinfo'].landing.content_object})
    if text:
        template = Template(text)
        return template.render(block_context)
    else:
        return ''