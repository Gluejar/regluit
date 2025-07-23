import logging

from django import template
from django.conf import settings


logger = logging.getLogger(__name__)

register = template.Library()

@register.simple_tag(takes_context=False)
def cf_site():
    return settings.CF_TURNSTILE_SITE_KEY
