# -*- coding: utf-8 -*-

from itertools import chain
from datetime import datetime, time

from django.shortcuts import render_to_response
from django.db.models import Q, Sum, Max, Min, Avg, Count
from django.template import RequestContext

from chartit import DataPool, Chart, PivotDataPool, PivotChart, RawDataPool

from core.models import IngresoDetalle, Ingreso, GastoDetalle, Gasto, Inversion, Proyecto, Municipio, TipoGasto, InversionFuente, InversionFuenteDetalle, CatInversion, ClasificacionMunicAno
from core.models import Anio, getYears
from core.models import PERIODO_INICIAL, PERIODO_ACTUALIZADO, PERIODO_FINAL, PERIODO_VERBOSE

def inversion_chart(municipio=None):
    municipio_list = Municipio.objects.all()
    year_list = getYears(Inversion)

    if municipio:
        source = Proyecto.objects.filter(inversion__periodo=PERIODO_INICIAL, inversion__municipio__slug=municipio). \
            values('year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_ultimos = Proyecto.objects.filter(inversion__periodo=PERIODO_INICIAL, inversion__municipio__slug=municipio, \
            inversion__year__gt=list(year_list)[-3]). \
            values('inversion__year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
    else:
        municipio = ''
        source = Proyecto.objects.filter(inversion__periodo=PERIODO_INICIAL). \
            values('inversion__year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_ultimos = Proyecto.objects.filter(inversion__periodo=PERIODO_INICIAL, inversion__year__gt=list(year_list)[-3]). \
            values('inversion__year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

    data_ultimos = DataPool(
           series=
            [{'options': {
                'source': source_ultimos,
                'categories': 'inversion__year',
                },
              'terms': ['inversion__year', 'ejecutado', 'asignado',]
            }],
    )
    chart_ultimos = Chart(
            datasource = data_ultimos,
            series_options =
              [{'options':{
                  'type': 'bar',
                  'stacking': False},
                'terms': {'inversion__year': ['asignado', 'ejecutado']}
                }],
            chart_options =
              {'title': {'text': u'Inversión por últimos años %s' % (municipio, )}},
            #x_sortf_mapf_mts = (None, lambda i:  i.strftime('%Y'), False)
    )
    data = DataPool(
           series=
            [{'options': {
                'source': source,
                'categories': 'inversion__year',
                },
              'terms': ['inversion__year', 'ejecutado', 'asignado',]
            }],
    )
    chart = Chart(
            datasource = data,
            series_options =
              [{'options':{
                  'type': 'bar',
                  'stacking': False},
                'terms': {'inversion__year': ['asignado', 'ejecutado']}
                }],
            chart_options =
              {'title': {'text': u'Inversión por años %s' % (municipio, )}},
            #x_sortf_mapf_mts = (None, lambda i:  i.strftime('%Y'), False)
    )
    return {'charts': (chart, chart_ultimos), 'municipio_list': municipio_list}


def inversion_categoria_chart(request):
    municipio_list = Municipio.objects.all()
    year_list = getYears(Inversion)
    year = year_list[-1]
    municipio = request.GET.get('municipio','')

    if municipio:
        source = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__year=year).values('catinversion__nombre').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('catinversion')
        source_ultimos = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__year__gt=year_list[-3]). \
            values('inversion__year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
    else:
        municipio = ''
        source = Proyecto.objects.filter(inversion__year=year).values('catinversion__nombre').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('catinversion')
        source_ultimos = Proyecto.objects.filter(inversion__year__gt=year_list[-3]). \
            values('inversion__year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

    data_ultimos = DataPool(
           series=
            [{'options': {
                'source': source_ultimos,
                'categories': 'inversion__year',
                },
              'terms': ['inversion__year', 'ejecutado', 'asignado',]
            }],
    )
    ultimos = Chart(
            datasource = data_ultimos,
            series_options =
              [{'options':{
                  'type': 'bar',
                  'stacking': False},
                'terms': {'inversion__year': ['asignado', 'ejecutado']}
                }],
            chart_options =
              {'title': {'text': u'Inversión por últimos años %s' % (municipio, )}},
    )
    oimdata = DataPool(
           series=
            [{'options': {'source': source },
              'terms': [
                'catinversion__nombre',
                'ejecutado',
                'asignado',
                ]}
             ])

    asignado = Chart(
            datasource = oimdata,
            series_options =
              [{'options':{
                  'type': 'pie',
                  },
                'terms':{
                  'catinversion__nombre': [
                    'asignado']
                  }}],
            chart_options =
              {'title': {
                  'text': 'Inversion asignados: %s %s' % (municipio, year,)},
                  'options3d': { 'enabled': 'true',  'alpha': '45', 'beta': '0' },
                  'plotOptions': { 'pie': { 'dataLabels': { 'enabled': False }, 'showInLegend': True, 'depth': 35}},
                  'tooltip': { 'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>' },
              })

    ejecutado = Chart(
            datasource = oimdata,
            series_options =
              [{'options':{
                  'type': 'pie',
                  },
                'terms':{
                  'catinversion__nombre': [
                    'ejecutado']
                  }}],
            chart_options =
              {'title': {
                  'text': 'Inversion ejecutados: %s %s' % (municipio, year,)},
                  'options3d': { 'enabled': 'true',  'alpha': '45', 'beta': '0' },
                  'plotOptions': { 'pie': { 'dataLabels': { 'enabled': False }, 'showInLegend': True, 'depth': 35}},
                  'tooltip': { 'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>' },
              })

    # tabla: get total and percent
    total = source.aggregate(total=Sum('asignado'))['total']
    for row in source:
        row['percent'] = round(row['asignado'] / total * 100, 0)

    # tabla: get ingresos por año
    porano_table = {}
    ys = source_ultimos.order_by('catinversion__nombre').values('catinversion__nombre').distinct()
    for y in ys:
        label = y['catinversion__nombre']
        porano_table[label] = {}
        for ayear in year_list:
            value = source_ultimos.filter(inversion__year=ayear, catinversion__nombre=label).aggregate(total=Sum('asignado'))['total']
            porano_table[label][ayear] = value if value else ''
        if municipio and year:
            periodo = PERIODO_FINAL
            quesumar = 'ejecutado'
            value = GastoDetalle.objects.filter(gasto__year=year, gasto__periodo=periodo, tipogasto__nombre=label, \
                    gasto__municipio__clasificaciones__clasificacion=mi_clasificacion.clasificacion, gasto__municipio__clase__anio=year).\
                    aggregate(total=Avg(quesumar))['total']
            porano_table[label]['extra'] = value if value else '...'

    return {'charts': (ejecutado, asignado, asignado_barra, barra), 'clasificacion': mi_clasificacion, 'anio': year, 'porano': porano_table, 'totales': source, 'year_list': year_list, 'municipio_list': municipio_list}
