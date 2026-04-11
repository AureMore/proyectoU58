from django import template

register = template.Library()

@register.filter
def formato_precio(precio):
    return "{:,.2f}".format(precio)