from regluit.utils.localdatetime import now
from django import template
from regluit.core.models import Acq
register = template.Library()

@register.simple_tag(takes_context=True)
def purchased(context):
    work = context['work']
    user = context['request'].user
    try: 
        user_license = work.get_user_licence(user)
        context['purchased'] = user_license.purchased
    except:
        context['purchased'] = False
    return ''
