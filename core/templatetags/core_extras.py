from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def million(number):
    return round(number / 1000000,2)

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
        return sum(float(d[key] or 0) for d in dict)
    except TypeError:
        return 0

@register.filter
def total_avg(dict, key):
    try:
        return sum(float(d[key] or 0) for d in dict) / len(dict)
    except TypeError:
        return 0

@register.inclusion_tag('descargar_excel.html')
def descargar_excel(reporte):
    return {'reporte': reporte}
