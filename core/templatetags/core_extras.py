from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def keyvalue(dict, key):
    try:
        return dict[key]
    except KeyError:
        if key.isdigit():
            return dict[int(key)]

@register.filter
def total_sum(dict, key):
    try:
        return sum(d[key] for d in dict)
    except TypeError:
        return 0

@register.filter
def total_avg(dict, key):
    try:
        return sum(d[key] for d in dict) / len(dict)
    except TypeError:
        return 0
