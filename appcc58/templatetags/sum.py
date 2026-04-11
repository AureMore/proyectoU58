from django import template
from decimal import Decimal, ROUND_DOWN

register = template.Library()

@register.filter
def sum_field(queryset, field):
    total = Decimal('0.0')  # Inicializa el total como Decimal
    for item in queryset:
        value = getattr(item, field)
        if value is not None:  # Asegúrate de que el valor no sea None
            total += Decimal(value)  # Convierte el valor a Decimal antes de sumarlo
    return total