from django import template
from main.main_utils import get_color_class

register = template.Library()

@register.filter
def score_color_class(score, max_points=5):
    return get_color_class(score, max_points)

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None  # or return dictionary if you want to fallback to the string itself

@register.filter
def has_scores(student):
    return bool(student.ufli_score_1 or student.ufli_score_2)

@register.filter
def any_scores(students):
    return any(s.ufli_score_1 or s.ufli_score_2 for s in students)



