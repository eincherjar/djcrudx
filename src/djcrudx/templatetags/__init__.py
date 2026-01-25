from django import template
from ..translations import smart_translate

register = template.Library()

@register.simple_tag
def trans(text):
    """Automatyczne tłumaczenie bez potrzeby makemessages"""
    return smart_translate(text)

@register.simple_tag  
def blocktrans(text, **kwargs):
    """Automatyczne tłumaczenie z parametrami"""
    translated = smart_translate(text)
    return translated.format(**kwargs)