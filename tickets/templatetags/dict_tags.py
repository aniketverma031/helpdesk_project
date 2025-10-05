# tickets/templatetags/dict_tags.py
from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Allows dictionary lookup by key in Django templates."""
    return dictionary.get(key)