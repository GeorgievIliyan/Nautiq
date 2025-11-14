from django import template
register = template.Library()

@register.filter(name='k_format')
def format_k_suffix(value):
    try:
        num = int(value) 
    except (ValueError, TypeError):
        return str(value)
    if num < 1000:
        return str(num)
    thousands = num / 1000.0
    formatted = "%.1f" % thousands
    if formatted.endswith(".0"):
        formatted = formatted[:-2]

    return formatted + 'k'