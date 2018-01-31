from django import template
from regluit.core.models import Campaign
from regluit.core.parameters import REWARDS, BUY2UNGLUE, THANKS

register = template.Library()

@register.simple_tag(takes_context=True)
def explore(context):
    context['top_pledge'] = Campaign.objects.filter(
        status="ACTIVE",
        type=REWARDS
    ).order_by('-work__id')[:4]
    context['top_b2u'] = Campaign.objects.filter(
        status="ACTIVE",
        type=BUY2UNGLUE
    ).order_by('-work__id')[:2]
    context['top_t4u'] = Campaign.objects.filter(
        status="ACTIVE",
        type=THANKS
    ).order_by('-work__id')[:4]

    return ''
