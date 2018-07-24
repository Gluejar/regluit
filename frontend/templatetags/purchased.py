from django import template
from django.utils.timezone import now

from regluit.core.models import Acq
register = template.Library()

@register.simple_tag(takes_context=True)
def purchased(context):
    work = context['work']
    try:
        work.id  # sometimes work is a dict
        user = context['request'].user
        if user.is_anonymous:
            return ''
        try:
            user_license = work.get_user_license(user)
            context['borrowable'] = work.borrowable(user)
            context['in_library'] = work.in_library(user)
            context['lib_thanked'] = work.lib_thanked(user)
        except AttributeError:
            user_license = None
            context['borrowable'] = None
            context['in_library'] = None
            holds = user.holds.filter(work=work)
            if holds.count():
                context['on_hold'] = holds[0]
        if user_license:
            context['purchased'] = user_license.purchased
            context['borrowed'] = user_license.borrowed
            context['license_is_active'] = user_license.is_active
        else:
            context['purchased'] = None
            context['borrowed'] = None
            context['license_is_active'] = False
    except AttributeError:
        pass
    return ''
