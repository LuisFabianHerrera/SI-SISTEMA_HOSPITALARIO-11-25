
# gestion_administrativa/templatetags/diccionario.py
from django import template

register = template.Library()

@register.filter
def dictget(d, key):
    return d.get(key, {})
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
from django import template

register = template.Library()

@register.filter
def dictget(d, key):
    """Obtiene un valor de diccionario con clave key."""
    return d.get(key)
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Obtiene un valor de diccionario con clave key"""
    return dictionary.get(key)

# gestion_administrativa/templatetags/diccionario.py
from django import template
register = template.Library()

@register.filter
def dictget(d, key):
    return d.get(key)

# gestion_administrativa/templatetags/diccionario.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
# gestion_administrativa/templatetags/diccionario.py
from django import template

register = template.Library()

@register.filter
def dictget(d, key):
    """Obtiene un valor de un diccionario usando la clave"""
    return d.get(key, '')
# gestion_administrativa/templatetags/diccionario.py
from django import template
register = template.Library()

@register.filter
def dictget(d, key):
    return d.get(key, '')

