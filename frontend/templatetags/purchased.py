from regluit.utils.localdatetime import now
from django import template
from regluit.core.models import Acq
register = template.Library()

@register.simple_tag(takes_context=True)
def purchased(context):
    work = context['work']
    user = context['request'].user
    try: 
        context['purchased'] = work.purchased_by(user)
    except:
        context['purchased'] = False
    return ''
