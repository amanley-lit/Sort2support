from django import template

register = template.Library()

@register.filter
def get_range(value):
    """Returns a range from 0 to value (inclusive)."""
    return range(int(value) + 1)