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
