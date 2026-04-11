from django import template

register = template.Library()

@register.filter
def duration_to_hours(duration):
    hours = duration.seconds // 3600
    minutes = (duration.seconds // 60) % 60
    return f"{hours} horas {minutes} minutos"

@register.filter
def zero_pad(value, width):
    return str(value).zfill(width)


@register.filter
def negate(value):
    return -value


@register.filter
def get_item(dictionary, key):
    if not dictionary:
        return None
    
    return dictionary.get(str(key))

# En tu archivo de templatetags/my_tags.py
@register.simple_tag
def get_dict_item(dictionary, key):
    if not dictionary:
        return None
    # Forzamos str(key) porque tu print mostró llaves como '1', '15' (strings)
    return dictionary.get(str(key))