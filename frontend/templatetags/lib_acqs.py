from django.utils.timezone import now
from django import template
register = template.Library()

@register.simple_tag(takes_context=True)
def lib_acqs(context):
    work = context['work']
    library = context.get('library',False)
    if library:
        lib_user = library.user
    else:
        user = context['request'].user
        if user.is_anonymous:
            return ''
        else:
            lib_user = (lib.user for lib in user.profile.libraries)
    try:
        user_license = work.get_user_license(lib_user)
    except AttributeError:
        user_license = None
    if user_license:
        context['lib_acqs'] = user_license.lib_acqs
        context['next_acq'] = user_license.next_acq
    else:
        context['lib_acqs'] = None
    
    return ''
