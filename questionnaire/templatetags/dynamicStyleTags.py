#!/usr/bin/python

from django import template
from ..models import DBStylesheet


register = template.Library()


@register.filter(name="getAssociatedStylesheets")
def getAssociatedStylesheets(inclusionTag):
    if DBStylesheet.objects.filter(inclusion_tag=inclusionTag).exists():
        return DBStylesheet.objects.get(inclusion_tag=inclusionTag).content
    else:
        return None
