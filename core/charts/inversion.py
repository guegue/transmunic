# -*- coding: utf-8 -*-

from itertools import chain
from datetime import datetime, time

from django.shortcuts import render_to_response
from django.db.models import Q, Sum, Max, Min, Avg, Count
from django.template import RequestContext

from chartit import DataPool, Chart, PivotDataPool, PivotChart, RawDataPool

from core.models import IngresoDetalle, Ingreso, Proyecto, Inversion, Inversion, Proyecto, Municipio, TipoProyecto, InversionFuente, InversionFuenteDetalle, CatInversion, ClasificacionMunicAno
from core.models import Anio, getYears
from core.models import PERIODO_INICIAL, PERIODO_ACTUALIZADO, PERIODO_FINAL, PERIODO_VERBOSE, AREAGEOGRAFICA_VERBOSE

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


##############################################################################
#
# Inversion charts /core/iversion-categoria FIXME: yep, mal nombre...
#
##############################################################################
def inversion_categoria_chart(municipio=None, year=None, portada=False):
    municipio_list = Municipio.objects.all()
    year_list = getYears(Inversion)
    if not year:
        year = year_list[-1]

    periodo = Anio.objects.get(anio=year).periodo
    quesumar = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'

    ChartError = False

    if municipio:
        source = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__year=year).values('catinversion__nombre').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('catinversion')
        source_ultimos = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__year__gt=year_list[-3]). \
            values('inversion__year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

        # obtiene clase y contador (otros en misma clase) para este año
        mi_clase = ClasificacionMunicAno.objects.get(municipio__slug=municipio, anio=year)
        mi_clase_count = ClasificacionMunicAno.objects.filter(clasificacion__clasificacion=mi_clase.clasificacion, anio=year).count()
        # obtiene clase y contador (otros en misma clase) para todos los años
        mi_clase_anios = list(ClasificacionMunicAno.objects.filter(municipio__slug=municipio).values('anio', 'clasificacion__clasificacion').annotate())
        mi_clase_anios_count = {}
        for aclase in mi_clase_anios:
            mi_clase_anios_count[aclase['anio']] = ClasificacionMunicAno.objects.filter(clasificacion__clasificacion=aclase['clasificacion__clasificacion'], anio=aclase['anio']).count()

        # obtiene datos para grafico comparativo de tipo de inversions
        tipo_inicial= list(Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__year=year, inversion__periodo=PERIODO_INICIAL).values('catinversion__nombre').annotate(asignado=Sum('asignado')))
        tipo_final = list(Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__year=year, inversion__periodo=PERIODO_FINAL).values('catinversion__nombre').annotate(ejecutado=Sum('ejecutado')))
        # decide si agarra el final y le agrega los iniciales (o al revés)
        if periodo == PERIODO_FINAL:
            for row in tipo_final:
                found = False
                for row2 in tipo_inicial:
                    if row2['catinversion__nombre'] == row['catinversion__nombre']:
                        row['asignado'] = row2['asignado']
                        found = True
                if not found:
                    row['asignado'] = 0
            tipo = tipo_final
        else:
            for row in tipo_inicial:
                found = False
                for row2 in tipo_final:
                    if row2['catinversion__nombre'] == row['catinversion__nombre']:
                        row['ejecutado'] = row2['ejecutado']
                        found = True
                if not found:
                    row['ejecutado'] = 0
            tipo = tipo_inicial

        # obtiene datos para grafico comparativo por area
        area_inicial= list(Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__year=year, inversion__periodo=PERIODO_INICIAL).values('areageografica').annotate(asignado=Sum('asignado')))
        area_final = list(Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__year=year, inversion__periodo=PERIODO_FINAL).values('areageografica').annotate(ejecutado=Sum('ejecutado')))
        # decide si agarra el final y le agrega los iniciales (o al revés)
        if periodo == PERIODO_FINAL:
            for row in area_final:
                found = False
                for row2 in area_inicial:
                    if row2['areageografica'] == row['areageografica']:
                        row['asignado'] = row2['asignado']
                        found = True
                if not found:
                    row['asignado'] = 0
            area = area_final
        else:
            for row in area_inicial:
                found = False
                for row2 in area_final:
                    if row2['areageografica'] == row['areageografica']:
                        row['ejecutado'] = row2['ejecutado']
                        found = True
                if not found:
                    row['ejecutado'] = 0
            area = area_inicial

        # obtiene datos para grafico comparativo por fuente
        fuente_inicial= list(InversionFuenteDetalle.objects.filter(inversionfuente__municipio__slug=municipio, inversionfuente__year=year, inversionfuente__periodo=PERIODO_INICIAL).values('fuente__nombre').annotate(asignado=Sum('asignado')))
        fuente_final = list(InversionFuenteDetalle.objects.filter(inversionfuente__municipio__slug=municipio, inversionfuente__year=year, inversionfuente__periodo=PERIODO_FINAL).values('fuente__nombre').annotate(ejecutado=Sum('ejecutado')))
        # decide si agarra el final y le agrega los iniciales (o al revés)
        if periodo == PERIODO_FINAL:
            for row in fuente_final:
                found = False
                for row2 in fuente_inicial:
                    if row2['fuente__nombre'] == row['fuente__nombre']:
                        row['asignado'] = row2['asignado']
                        found = True
                if not found:
                    row['asignado'] = 0
            fuente = fuente_final
        else:
            for row in fuente_inicial:
                found = False
                for row2 in fuente_final:
                    if row2['fuente__nombre'] == row['fuente__nombre']:
                        row['ejecutado'] = row2['ejecutado']
                        found = True
                if not found:
                    row['ejecutado'] = 0
            fuente = fuente_inicial

        # obtiene datos para OIM comparativo de todos los años
        inicial = list(Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__periodo=PERIODO_INICIAL).values('inversion__year', 'inversion__periodo').annotate(municipio_inicial=Sum('asignado')))
        final = list(Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__periodo=PERIODO_FINAL).values('inversion__year', 'inversion__periodo').annotate(municipio_final=Sum('ejecutado')))

        # obtiene datos para municipio de la misma clase
        inicial_clase = Proyecto.objects.filter(inversion__periodo=PERIODO_INICIAL,\
                inversion__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, inversion__municipio__clase__anio=year).\
                values('inversion__year', 'inversion__periodo').order_by('inversion__periodo').annotate(clase_inicial=Sum('asignado'))
        final_clase = Proyecto.objects.filter(inversion__periodo=PERIODO_FINAL,\
                inversion__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, inversion__municipio__clase__anio=year).\
                values('inversion__year', 'inversion__periodo').order_by('inversion__periodo').annotate(clase_final=Sum('ejecutado'))

        for row in inicial:
            for row2 in inicial_clase:
                if row2['inversion__year'] == row['inversion__year']:
                    row['clase_inicial'] = row2['clase_inicial'] / mi_clase_anios_count[row['inversion__year']]
        for row in final:
            for row2 in final_clase:
                if row2['inversion__year'] == row['inversion__year']:
                    row['clase_final'] = row2['clase_final'] / mi_clase_anios_count[row['inversion__year']]
        for row in inicial:
            found = False
            for row2 in final:
                if row2['inversion__year'] == row['inversion__year']:
                    found = True
                    row['clase_final'] = row2['clase_final'] / mi_clase_anios_count[row['inversion__year']]
                    row['municipio_final'] = row2['municipio_final']
                if not found:
                    row['clase_final'] = 0
                    row['municipio_final'] = 0
        comparativo_anios = inicial

    else:
        municipio = ''
        source = Proyecto.objects.filter(inversion__year=year).values('catinversion__nombre').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('catinversion')
        source_ultimos = Proyecto.objects.filter(inversion__year__gt=year_list[-3]). \
            values('inversion__year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

        # obtiene datos para grafico comparativo de tipo de inversions
        tipo_inicial= list(Proyecto.objects.filter(inversion__year=year, inversion__periodo=PERIODO_INICIAL).values('catinversion__nombre').order_by('catinversion__nombre').annotate(asignado=Sum('asignado')))
        tipo_final = list(Proyecto.objects.filter(inversion__year=year, inversion__periodo=PERIODO_FINAL).values('catinversion__nombre').order_by('catinversion__nombre').annotate(ejecutado=Sum('ejecutado')))
        for row in tipo_inicial:
            found = False
            for row2 in tipo_final:
                if row2['catinversion__nombre'] == row['catinversion__nombre']:
                    found = True
                    row['ejecutado'] = row2['ejecutado']
            if not found:
                row['ejecutado'] = 0
        tipo = tipo_inicial

        # obtiene datos para grafico comparativo de area
        area_inicial= list(Proyecto.objects.filter(inversion__year=year, inversion__periodo=PERIODO_INICIAL).values('areageografica').order_by('areageografica').annotate(asignado=Sum('asignado')))
        area_final = list(Proyecto.objects.filter(inversion__year=year, inversion__periodo=PERIODO_FINAL).values('areageografica').order_by('areageografica').annotate(ejecutado=Sum('ejecutado')))
        for row in area_inicial:
            found = False
            for row2 in area_final:
                if row2['areageografica'] == row['areageografica']:
                    found = True
                    row['ejecutado'] = row2['ejecutado']
            if not found:
                row['ejecutado'] = 0
        area = area_inicial

        # obtiene datos para grafico comparativo de fuente
        fuente_inicial= list(InversionFuenteDetalle.objects.filter(inversionfuente__year=year, inversionfuente__periodo=PERIODO_INICIAL).values('fuente__nombre').order_by('fuente__nombre').annotate(asignado=Sum('asignado')))
        fuente_final = list(InversionFuenteDetalle.objects.filter(inversionfuente__year=year, inversionfuente__periodo=PERIODO_FINAL).values('fuente__nombre').order_by('fuente__nombre').annotate(ejecutado=Sum('ejecutado')))
        for row in fuente_inicial:
            found = False
            for row2 in fuente_final:
                if row2['fuente__nombre'] == row['fuente__nombre']:
                    found = True
                    row['ejecutado'] = row2['ejecutado']
            if not found:
                row['ejecutado'] = 0
        fuente = fuente_inicial

    # conviert R en Rural, etc.
    for d in area:
        d.update((k, AREAGEOGRAFICA_VERBOSE[v]) for k, v in d.iteritems() if k == "areageografica")

    if municipio:
        inversion_comparativo_anios = RawDataPool(
            series=
                [{'options': {'source': comparativo_anios },
                'terms':  ['inversion__year','inversion__periodo','municipio_inicial','municipio_final','clase_inicial','clase_final'],
                }],
            )
        inversion_comparativo_anios_column = Chart(
                datasource = inversion_comparativo_anios,
                series_options =
                [{'options':{
                    'type': 'column',
                    'stacking': False},
                    'terms':{
                    'inversion__year': ['municipio_inicial', 'clase_inicial', 'municipio_final', 'clase_final'],
                    },
                    }],
                chart_options =
                {'title': { 'text': 'Inversiones %s' % (municipio,)}},
                )
    inversion_fuente = RawDataPool(
        series=
            [{'options': {'source': fuente },
            'terms':  ['fuente__nombre','ejecutado','asignado'],
            }],
        )
    inversion_fuente_column = Chart(
            datasource = inversion_fuente,
            series_options =
            [{'options':{
                'type': 'column',
                'stacking': False},
                'terms':{
                'fuente__nombre': ['ejecutado', 'asignado'],
                },
                }],
            chart_options =
            {
                'title': { 'text': 'Inversions por fuente origen %s %s' % (year, municipio,)},
                'data': { 'table': 'datatable'},
            },
    )
    inversion_area = RawDataPool(
        series=
            [{'options': {'source': area },
            'terms':  ['areageografica','ejecutado','asignado'],
            }],
        )
    inversion_area_column = Chart(
            datasource = inversion_area,
            series_options =
            [{'options':{
                'type': 'column',
                'stacking': False},
                'terms':{
                'areageografica': ['ejecutado', 'asignado'],
                },
                }],
            chart_options =
            {
                'title': { 'text': 'Inversions por area origen %s %s' % (year, municipio,)},
                'data': { 'table': 'datatable'},
            },
    )
    inversion_tipo = RawDataPool(
        series=
            [{'options': {'source': tipo },
            'terms':  ['catinversion__nombre','ejecutado','asignado'],
            }],
        )
    inversion_tipo_column = Chart(
            datasource = inversion_tipo,
            series_options =
            [{'options':{
                'type': 'column',
                'stacking': False},
                'terms':{
                'catinversion__nombre': ['ejecutado', 'asignado'],
                },
                }],
            chart_options =
            {
                'title': { 'text': 'Inversions por tipo origen %s %s' % (year, municipio,)},
                'data': { 'table': 'datatable'},
            },
    )
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

    # tabla: get inversions por año
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
            value = Proyecto.objects.filter(inversion__year=year, inversion__periodo=periodo, tipoproyecto__nombre=label, \
                    inversion__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, inversion__municipio__clase__anio=year).\
                    aggregate(total=Avg(quesumar))['total']
            porano_table[label]['extra'] = value if value else '...'

    mi_clase = None

    if portada:
        charts =  (ejecutado, )
    elif municipio:
        charts =  (inversion_tipo_column, inversion_area_column, inversion_fuente_column, inversion_comparativo_anios_column, ejecutado, asignado, ultimos )
    else:
        charts =  (ejecutado, asignado, ultimos )

    return {'charts': charts, \
        'clasificacion': mi_clase, 'anio': year, 'porano': porano_table, 'totales': source, \
        'year_list': year_list, 'municipio_list': municipio_list, 'municipio': municipio}
