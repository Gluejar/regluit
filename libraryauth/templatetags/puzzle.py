from random import randint

from django.template import Library

register = Library()

@register.simple_tag(takes_context=True)
def puzz(context):
    num1 = randint(0, 10)
    num2 = randint(0, 10)
    context['puzznum1'] = num1
    context['puzznum2'] = num2
    context['puzzans'] = num1 + num2
    return ''
