# gestion_administrativa/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    """Obtiene el valor de un diccionario usando key"""
    return d.get(key)
