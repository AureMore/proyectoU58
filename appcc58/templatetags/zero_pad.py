from django import template

register = template.Library()

@register.filter
def zero_pad(value, width):
    return str(value).zfill(width)