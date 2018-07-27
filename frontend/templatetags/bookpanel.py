from django import template
from django.utils.timezone import now

from regluit.core.parameters import REWARDS, BUY2UNGLUE

register = template.Library()

@register.simple_tag(takes_context=True)
def bookpanel(context):
    work = context['work']
    library = context.get('library',None)
    user = context['request'].user
    campaign = context.get('last_campaign', None)

    # compute a boolean that's true if bookpanel should show a "pledge" button...
    # campaign is ACTIVE, type 1 - REWARDS
    # user has not pledged or user is anonymous

    supported = False
    if campaign and campaign.type == REWARDS:
        if campaign.status == 'ACTIVE':
            if not user.is_anonymous and user.transaction_set.filter(campaign__work=work):
                supported = True
    context['supported'] = supported

    show_pledge = False
    if campaign and campaign.type == REWARDS:
        if campaign.status == 'ACTIVE':
            if user.is_anonymous or not supported:
                show_pledge = True
    context['show_pledge'] = show_pledge

    # compute a boolean that's true if bookpanel should show a "purchase" button...
    # campaign is ACTIVE, type 2 - BUY2UNGLUE
    # user has not purchased or user is anonymous
    # user has not borrowed or user is anonymous
    # work not available in users library
    # not on the library page

    show_purchase = False
    if campaign and campaign.type == BUY2UNGLUE:
        if user.is_anonymous or not context.get('license_is_active', False):
            if campaign.status == 'ACTIVE':
                if not context.get('borrowable', False):
                    if not library:
                        show_purchase = True
    context['show_purchase'] = show_purchase
    return ''
