from random import randint

from django.core.cache import cache
from django.template import Library

register = Library()

digits = {
    0: '⓪',
    1: '1',
    2: '⓶',
    3: '③',
    4: '⑷',
    5: '⒌',
    6: 'six',
    7: '⑦',
    8: '8️⃣',
    9: '𝟫',
    10: '10',
}
encode_answers = cache.get('encode_answers')

@register.simple_tag(takes_context=True)
def puzz(context):
    num1 = randint(0, 10)
    num2 = randint(0, 10)
    context['puzznum1'] = digits[num1]
    context['puzznum2'] = digits[num2]
    context['puzzans'] = encode_answers[num1 + num2]
    return ''
