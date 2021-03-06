# -*- coding: UTF-8 -*-

import collections
import decimal
from django.conf import settings

from chartit import Chart, RawDataPool

colorscheme = settings.CHARTS_COLORSCHEME
colors_array = settings.COLORS_ARRAY
chart_options = settings.CHART_OPTIONS


def xnumber(number):
    if not number:
        return 0
    if isinstance(number, int) or isinstance(number, float):
        return number
    if str(number).isdigit():
        return int(number)
    if isinstance(number, basestring):
        # uses default comma
        comma = settings.THOUSAND_SEPARATOR

        # point character equals comma, so reverse
        if len(number) >= 3 and number[-3] == comma:
            reverse = {'.': ',', ',': '.'}
            point = number[-3]
            comma = reverse[point]
            number = number.replace(point, comma)

        number = number.replace(comma, '')
    try:
        return decimal.Decimal(number)
    except:
        return 0


def percentage(dividend, divider, decimals=1):
    if not dividend:
        return 0
    if not divider:
        return 0
    if divider == 0:
        return 0

    return round(dividend / xnumber(divider) * 100, decimals)


def getPeriods(model):  # ;)
    "Gets all years and their period with data from a model.anio"

    from models import Anio
    years = model.objects.values_list('anio').order_by('anio').distinct('anio')
    years = [x[0] for x in years]
    alist = {}
    for year in years:
        alist[str(year)] = Anio.objects.get(anio=year).periodo
    # return {x[0]:x[1] for x in years}
    return alist


def getYears(model):
    "Gets all years with data from a model.anio"

    years = model.objects.values_list('anio').order_by('anio').distinct('anio')
    return [x[0] for x in years]


def glue(inicial, final, key, actualizado=[]):
    "Glues together two different lists of 'asignado' and 'ejecutado' of dictionaries using a chosen key"

    merged = {}

    # cast as lists
    actualizado = list(actualizado)
    inicial = list(inicial)
    final = list(final)

    # changes 'asignado' to 'actualizado' #FIXME why not fix this at origin?
    for item in actualizado:
        item['actualizado'] = item.pop('asignado')
        # changes 'asignado_porcentaje' to 'asignado_porcentaje'
        if 'asignado_porcentaje' in item.keys():
            item['actualizado_porcentaje'] = item.pop('asignado_porcentaje')
    # do glue
    for item in inicial + final + actualizado:
        if item[key]:
            if item[key] in merged:
                merged[item[key]].update(item)
            else:
                merged[item[key]] = item
    omerged = collections.OrderedDict(sorted(merged.items()))
    glued = [val for (_, val) in omerged.iteritems()]

    # checks all required keys have a value (0 if none)
    required = ('ejecutado', 'actualizado', 'asignado')
    for item in glued:
        for r in required:
            if not r in item:
                item[r] = 0

    return glued


def growthRate(current_year, previus_year, years):
    "Contains the formula to calculate the growth rate"
    return (pow(current_year / previus_year,
                decimal.Decimal(1.0 / years)) - 1) * 100


def calculate_ep(total_ejecutado, total_presupuestado):
    if not total_ejecutado:
        return 0
    if not total_presupuestado:
        return 0
    if total_ejecutado == 0:
        return 0

    return ((total_ejecutado / total_presupuestado) - 1) * 100


def superglue(data=(), key='id', default=0):
    "Glues together different lists of dictionaries using a common key"

    alldata = []
    for datum in data:
        # cast as lists
        datum = list(datum)
        alldata = alldata + datum

    # do glue
    nonkeys = []
    merged = {}
    key_nombre_rubro = ''
    if len(alldata) > 0:
        for llave in alldata[0].keys():
            if 'nombre' in llave:
                key_nombre_rubro = llave

    for item in alldata:

        if not item[key] and item[key] != 0:
            item[key] = 'Sin Clasificar'
            item['subsubtipoingreso__origen__nombre'] = 'Sin Clasificar'
            item[key_nombre_rubro] = 'Sin Clasificar'

        if item[key] in merged:
            merged[item[key]].update(item)
        else:
            merged[item[key]] = item
        for field, value in item.iteritems():
            if field <> key and field not in nonkeys:
                nonkeys.append(field)
    omerged = collections.OrderedDict(sorted(merged.items()))
    glued = [val for (_, val) in omerged.items()]

    # checks all required keys have a value (default if none)
    required = nonkeys
    for item in glued:
        for r in required:
            if not r in item:
                item[r] = default
    return glued


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"

    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]
