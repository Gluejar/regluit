"""
Template tags for amazon_fps
"""
from django import template
from billing.templatetags.amazon_fps_tags import amazon_fps
register = template.Library()

register.tag(amazon_fps)