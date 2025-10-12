from django import template

register = template.Library()

@register.filter
def get_range(value):
    """Return a range from 0 to value (inclusive)."""
    try:
        return range(int(value) + 1)
    except (ValueError, TypeError):
        return []