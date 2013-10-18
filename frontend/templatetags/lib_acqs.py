from regluit.utils.localdatetime import now
from django import template
register = template.Library()

@register.simple_tag(takes_context=True)
def lib_acqs(context):
    work = context['work']
    library = context.get('library',False)
    if not library:
        return ''
    user_license = work.get_user_license(library.user)
    if user_license:
        context['lib_acqs'] = user_license.lib_acqs
    else:
        context['lib_acqs'] = None
    return ''
