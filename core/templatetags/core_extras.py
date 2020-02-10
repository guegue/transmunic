from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def million(number):
    if number:
        return round(number / 1000000,2)
    else:
        return 0

@register.filter
def keyvalue(dict, key):
    key=str(key)
    if key in dict:
        return dict[key]
    if key.isdigit() and int(key) in dict:
        return dict[int(key)]
    return 'KeyError'

@register.filter
def total_sum(dict, key):
    try:
        return sum(float(d[key] or 0) for d in dict)
    except TypeError:
        return 0
    except KeyError:
        return 0

@register.filter
def total_avg(dict, key):
    try:
        return sum(float(d[key] or 0) for d in dict) / len(dict)
    except TypeError:
        return 0


@register.filter
def get_name_municipio(item):
    nombre = ''
    for key in item:
        if 'nombre' in key:
            nombre = item.get(key, '')
            break
    return nombre


@register.inclusion_tag('descargar_excel.html')
def descargar_excel(reporte):
    return {'reporte': reporte}
