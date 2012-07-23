"""
The truncatechars filter is part of Django dev, but we're on 1.3.1
The following is the filter and its dependencies
To use this filter, put "{% load truncatechars %}" at the beginning of your template, 
then {{ myvariable|truncatechars:num }}
"""
import unicodedata
from django.template.base import Library
from django.template.defaultfilters import stringfilter
from django.utils.translation import get_language_info

register = Library()

custom_language_info = {'xx': {'name':'unknown', 'name_local':'unknown'},
                        'un': {'name':'??', 'name_local':'??'},
                        'zh': {'name':'chinese', 'name_local':u'\u4E2D\u6587'},
                        'la': {'name':'Latin', 'name_local':'LATINA'},
                        'ut': {'name':u'\u00DCttish', 'name_local':u'\u00DCttish'},
                        }
                        
        
# need to not throw exceptions when no built-in lang yet     
@register.filter()
@stringfilter
def ez_lang_name(value):
    """
    returns language name  without throwing exceptions.
    """
    try:
        try:
            li = get_language_info( value )
        except KeyError: # Invalid literal for int().
            li = custom_language_info[ value ]
        return li['name']
    except KeyError:
        return value

# need to not throw exceptions when no built-in lang yet     
@register.filter()
@stringfilter
def ez_lang_name_local(value):
    """
    returns language name in its language without throwing exceptions.
    """
    try:
        try:
            li = get_language_info( value )
        except KeyError: # Invalid literal for int().
            li = custom_language_info[ value ]
        return li['name_local']
    except KeyError:
        return value
    