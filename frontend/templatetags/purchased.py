from regluit.utils.localdatetime import now
from django import template
from regluit.core.models import Acq
register = template.Library()

@register.simple_tag(takes_context=True)
def purchased(context):
    work = context['work']
    user = context['request'].user
    if user.is_anonymous():
        return ''
    user_license = work.get_user_license(user)
    if user_license:
        context['purchased'] = user_license.purchased
        context['borrowed'] = user_license.borrowed
        context['license_is_active'] = user_license.is_active
    else:
        context['purchased'] = None
        context['borrowed'] = None
        context['license_is_active'] = False
    borrowable = False
    for library in user.profile.libraries:
        lib_license=work.get_user_license(library.user)
        if lib_license and lib_license.borrowable:
            borrowable = True
            continue
    context['borrowable'] = borrowable
    return ''
