from django import template
from django.conf import settings
from ..translations import smart_translate

register = template.Library()

@register.simple_tag
def get_base_template():
    """Pobierz base template z ustawień Django"""
    return getattr(settings, 'DJCRUDX_BASE_TEMPLATE', 'crud/base.html')

@register.simple_tag
def trans(text):
    """Uniwersalne tłumaczenie - Django i18n > custom > fallback"""
    return smart_translate(text)

@register.simple_tag  
def blocktrans(text, **kwargs):
    """Uniwersalne tłumaczenie z parametrami"""
    translated = smart_translate(text)
    return translated.format(**kwargs)