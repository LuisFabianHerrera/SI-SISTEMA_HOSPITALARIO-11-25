# dict_extras.py
from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def add_key(empleado_id, fecha):
    return (empleado_id, fecha)
