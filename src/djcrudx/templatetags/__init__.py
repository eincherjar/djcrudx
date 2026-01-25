from django import template
from ..translations import auto_translate

register = template.Library()

@register.simple_tag
def trans(text):
    """Automatyczne tłumaczenie bez potrzeby makemessages"""
    return auto_translate(text)

@register.simple_tag  
def blocktrans(text, **kwargs):
    """Automatyczne tłumaczenie z parametrami"""
    translated = auto_translate(text)
    return translated.format(**kwargs)