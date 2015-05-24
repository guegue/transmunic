# -*- coding: utf-8 -*-
##############################################################################
#
# OGM charts /core/ogm
#
##############################################################################

from itertools import chain
from datetime import datetime, time

from django.shortcuts import render_to_response
from django.db.models import Q, Sum, Max, Min, Avg, Count
from django.template import RequestContext

from chartit import DataPool, Chart, PivotDataPool, PivotChart, RawDataPool

from core.models import GastoDetalle, Gasto, GastoDetalle, Gasto, Inversion, Proyecto, Municipio, TipoGasto, InversionFuente, InversionFuenteDetalle, CatInversion, ClasificacionMunicAno
from core.models import Anio, getYears
from core.models import PERIODO_INICIAL, PERIODO_ACTUALIZADO, PERIODO_FINAL, PERIODO_VERBOSE

def ogm_chart(municipio=None, year=None, portada=False):
    municipio_list = Municipio.objects.all()
    year_list = getYears(Gasto)
    if not year:
        year = year_list[-1]

    periodo = Anio.objects.get(anio=year).periodo
    quesumar = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'

    ChartError = False

    if municipio:
        source = GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__year=year).values('subsubtipogasto__origen__nombre').annotate(ejecutado=Sum(quesumar)).order_by('subsubtipogasto__origen__nombre')
        source_barra = GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=periodo, gasto__year__gt=year_list[-3])
        source_pivot = GastoDetalle.objects.filter(gasto__periodo=periodo, gasto__municipio__slug=municipio)

        # obtiene clase y contador (otros en misma clase) para este año
        mi_clase = ClasificacionMunicAno.objects.get(municipio__slug=municipio, anio=year)
        mi_clase_count = ClasificacionMunicAno.objects.filter(clasificacion__clasificacion=mi_clase.clasificacion, anio=year).count()
        # obtiene clase y contador (otros en misma clase) para todos los años
        mi_clase_anios = list(ClasificacionMunicAno.objects.filter(municipio__slug=municipio).values('anio', 'clasificacion__clasificacion').annotate())
        mi_clase_anios_count = {}
        for aclase in mi_clase_anios:
            mi_clase_anios_count[aclase['anio']] = ClasificacionMunicAno.objects.filter(clasificacion__clasificacion=aclase['clasificacion__clasificacion'], anio=aclase['anio']).count()

        # obtiene datos para grafico comparativo de tipo de gastos
        tipo_inicial= list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__year=year, gasto__periodo=PERIODO_INICIAL).values('subsubtipogasto__origen__nombre').annotate(asignado=Sum('asignado')))
        tipo_final = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__year=year, gasto__periodo=PERIODO_FINAL).values('subsubtipogasto__origen__nombre').annotate(ejecutado=Sum('ejecutado')))
        # decide si agarra el final y le agrega los iniciales (o al revés)
        if periodo == PERIODO_FINAL:
            for row in tipo_final:
                found = False
                for row2 in tipo_inicial:
                    if row2['subsubtipogasto__origen__nombre'] == row['subsubtipogasto__origen__nombre']:
                        row['asignado'] = row2['asignado']
                        found = True
                if not found:
                    row['asignado'] = 0
            tipo = tipo_final
        else:
            for row in tipo_inicial:
                found = False
                for row2 in tipo_final:
                    if row2['subsubtipogasto__origen__nombre'] == row['subsubtipogasto__origen__nombre']:
                        row['ejecutado'] = row2['ejecutado']
                        found = True
                if not found:
                    row['ejecutado'] = 0
            tipo = tipo_inicial

        # obtiene datos para OIM comparativo de todos los años
        inicial = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL).values('gasto__year', 'gasto__periodo').annotate(municipio_inicial=Sum('asignado')))
        final = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_FINAL).values('gasto__year', 'gasto__periodo').annotate(municipio_final=Sum('ejecutado')))

        # obtiene datos para municipio de la misma clase
        inicial_clase = GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL,\
                gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, gasto__municipio__clase__anio=year).\
                values('gasto__year', 'gasto__periodo').order_by('gasto__periodo').annotate(clase_inicial=Sum('asignado'))
        final_clase = GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL,\
                gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, gasto__municipio__clase__anio=year).\
                values('gasto__year', 'gasto__periodo').order_by('gasto__periodo').annotate(clase_final=Sum('ejecutado'))

        for row in inicial:
            for row2 in inicial_clase:
                if row2['gasto__year'] == row['gasto__year']:
                    row['clase_inicial'] = row2['clase_inicial'] / mi_clase_anios_count[row['gasto__year']]
        for row in final:
            for row2 in final_clase:
                if row2['gasto__year'] == row['gasto__year']:
                    row['clase_final'] = row2['clase_final'] / mi_clase_anios_count[row['gasto__year']]
        for row in inicial:
            found = False
            for row2 in final:
                if row2['gasto__year'] == row['gasto__year']:
                    found = True
                    row['clase_final'] = row2['clase_final'] / mi_clase_anios_count[row['gasto__year']]
                    row['municipio_final'] = row2['municipio_final']
                if not found:
                    row['clase_final'] = 0
                    row['municipio_final'] = 0
        comparativo_anios = inicial
        #FIXME: no longer? comparativo_anios = list(chain(inicial, final, ))

        # obtiene datos para OIM comparativo de un año específico
        inicial = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__year=year, gasto__periodo=PERIODO_INICIAL).values('gasto__periodo').annotate(municipio=Sum('asignado')))
        actualizado = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__year=year, gasto__periodo=PERIODO_ACTUALIZADO).values('gasto__periodo').annotate(municipio=Sum('ejecutado')))
        final = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__year=year, gasto__periodo=PERIODO_FINAL).values('gasto__periodo').annotate(municipio=Sum('ejecutado')))

        # obtiene datos para municipio de la misma clase
        inicial_clase = GastoDetalle.objects.filter(gasto__year=year, gasto__periodo=PERIODO_INICIAL,\
                gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, gasto__municipio__clase__anio=year).\
                values('gasto__periodo').order_by('gasto__periodo').annotate(clase=Sum('asignado'))
        actualizado_clase = GastoDetalle.objects.filter(gasto__year=year, gasto__periodo=PERIODO_ACTUALIZADO,\
                gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, gasto__municipio__clase__anio=year).\
                values('gasto__periodo').order_by('gasto__periodo').annotate(clase=Sum('ejecutado'))
        final_clase = GastoDetalle.objects.filter(gasto__year=year, gasto__periodo=PERIODO_FINAL,\
                gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, gasto__municipio__clase__anio=year).\
                values('gasto__periodo').order_by('gasto__periodo').annotate(clase=Sum('ejecutado'))

        # inserta datos para municipio de la misma clase
        if inicial:
            inicial[0]['clase'] = inicial_clase[0]['clase'] / mi_clase_count
        if actualizado:
            actualizado[0]['clase'] = actualizado_clase[0]['clase'] / mi_clase_count * 10000 # FIXME: testing * 10000
            actualizado[0]['municipio'] *= 10000 # FIXME: testing * 10000
        if final:
            final[0]['clase'] = final_clase[0]['clase'] / mi_clase_count
        comparativo3 = list(chain(inicial, actualizado, final))
        comparativo2 = list(chain(inicial, final, ))
        for d in comparativo3:
            d.update((k, PERIODO_VERBOSE[v]) for k, v in d.iteritems() if k == "gasto__periodo")
    else:
        mi_clase = None
        municipio = ''
        source = GastoDetalle.objects.filter(gasto__year=year, gasto__periodo=periodo).values('subsubtipogasto__origen__nombre').annotate(ejecutado=Sum(quesumar)).order_by('subsubtipogasto__origen__nombre')
        source_barra = GastoDetalle.objects.filter(gasto__periodo=periodo, gasto__year__gt=year_list[-3])
        source_pivot = GastoDetalle.objects.filter(gasto__periodo=periodo)

        source = GastoDetalle.objects.filter(gasto__year=year, gasto__periodo=periodo).values('subsubtipogasto__origen__nombre').annotate(ejecutado=Sum(quesumar)).order_by('subsubtipogasto__origen')
        source_barra = GastoDetalle.objects.filter(gasto__periodo=periodo)
        source_barra2 = GastoDetalle.objects.filter(gasto__periodo=periodo, gasto__year__gt=year_list[-3])
        comparativo = GastoDetalle.objects.filter(gasto__periodo='')
        
        # obtiene datos para grafico comparativo de tipo de gastos
        tipo_inicial= list(GastoDetalle.objects.filter(gasto__year=year, gasto__periodo=PERIODO_INICIAL).values('subsubtipogasto__origen__nombre').order_by('subsubtipogasto__origen__nombre').annotate(asignado=Sum('asignado')))
        tipo_final = list(GastoDetalle.objects.filter(gasto__year=year, gasto__periodo=PERIODO_FINAL).values('subsubtipogasto__origen__nombre').order_by('subsubtipogasto__origen__nombre').annotate(ejecutado=Sum('ejecutado')))
        for row in tipo_inicial:
            found = False
            for row2 in tipo_final:
                if row2['subsubtipogasto__origen__nombre'] == row['subsubtipogasto__origen__nombre']:
                    found = True
                    row['ejecutado'] = row2['ejecutado']
            if not found:
                row['ejecutado'] = 0
        tipo = tipo_inicial

    if municipio:
        ogm_comparativo_anios = RawDataPool(
            series=
                [{'options': {'source': comparativo_anios },
                'terms':  ['gasto__year','gasto__periodo','municipio_inicial','municipio_final','clase_inicial','clase_final'],
                }],
            )
        ogm_comparativo2 = RawDataPool(
            series=
                [{'options': {'source': comparativo2 },
                'terms':  ['gasto__periodo','municipio','clase'],
                }],
                #sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
                )
        ogm_comparativo3 = RawDataPool(
            series=
                [{'options': {'source': comparativo3 },
                'terms':  ['gasto__periodo','municipio','clase'],
                }],
                #sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
                )
        ogm_comparativo_anios_column = Chart(
                datasource = ogm_comparativo_anios,
                series_options =
                [{'options':{
                    'type': 'column',
                    'stacking': False},
                    'terms':{
                    'gasto__year': ['municipio_inicial', 'clase_inicial', 'municipio_final', 'clase_final'],
                    },
                    }],
                chart_options =
                {'title': { 'text': 'gastos %s' % (municipio,)}},
                )
        ogm_comparativo2_column = Chart(
                datasource = ogm_comparativo2,
                series_options =
                [{'options':{
                    'type': 'column',
                    'stacking': False},
                    'terms':{
                    'gasto__periodo': ['municipio', 'clase']
                    },
                    }],
                chart_options =
                {'title': { 'text': 'gastos %s %s' % (municipio, year)}},
                )
        ogm_comparativo3_column = Chart(
                datasource = ogm_comparativo3,
                series_options =
                [{'options':{
                    'type': 'column',
                    'stacking': False},
                    'terms':{
                    'gasto__periodo': ['municipio','clase']
                    },
                    }],
                chart_options =
                {'title': { 'text': 'gastos %s %s' % (municipio, year)}},
                )

    ogm_tipo = RawDataPool(
        series=
            [{'options': {'source': tipo },
            'terms':  ['subsubtipogasto__origen__nombre','ejecutado','asignado'],
            }],
        )
    ogm_tipo_column = Chart(
            datasource = ogm_tipo,
            series_options =
            [{'options':{
                'type': 'column',
                'stacking': False},
                'terms':{
                'subsubtipogasto__origen__nombre': ['ejecutado', 'asignado'],
                },
                }],
            chart_options =
            {
                'title': { 'text': 'Gastos por tipo origen %s %s' % (year, municipio,)},
                'data': { 'table': 'datatable'},
            },
    )
    pivot_barra = PivotDataPool(
           series=
            [{'options': {'source': source_pivot,
                        'categories': 'gasto__year',
                        'legend_by': 'subsubtipogasto__origen__nombre', },
              'terms': {
                  'ejecutado':Sum('ejecutado'),
                }
              }],
            #sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
            )
    asignado_barra = PivotChart(
            datasource = pivot_barra,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': 'percent'},
                'terms':['ejecutado']
                }],
            chart_options = {
              'title': { 'text': 'Gastos %s por tipo %s' % (quesumar, municipio,)},
              'options3d': { 'enabled': 'true',  'alpha': 10, 'beta': 10, 'depth': 50 },
            },
    )
    ogmdata_barra = PivotDataPool(
           series=
            [{'options': {'source': source_barra,
                        'categories': 'gasto__year',
                         },
              'terms': {
                  'ejecutado':Sum('ejecutado'),
                }
              }],
            )
    barra = PivotChart(
            datasource = ogmdata_barra,
            series_options =
              [{'options':{
                  'type': 'column',
                },
                'terms':['ejecutado']
                }],
            chart_options = {
              'title': { 'text': 'Gastos por periodo %s' % (municipio,)},
              'options3d': { 'enabled': 'true',  'alpha': 10, 'beta': 10, 'depth': 50 },
            }
    )
    ogmdata = DataPool(
           series=
            [{'options': {'source': source },
              'terms': [
                'subsubtipogasto__origen__nombre',
                'ejecutado',
                ]}
             ])

    asignado = Chart(
            datasource = ogmdata,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'subsubtipogasto__origen__nombre': [
                    'ejecutado']
                  }}],
            chart_options = {
                'title': { 'text': 'Destino del gasto %s %s' % (municipio, year,)},
                'options3d': { 'enabled': 'true',  'alpha': '45', 'beta': '0' },
                'plotOptions': { 'pie': { 'dataLabels': { 'enabled': False }, 'showInLegend': True, 'depth': 35}},
                'tooltip': { 'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>' },
            }
    )

    ejecutado = Chart(
            datasource = ogmdata,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'subsubtipogasto__origen__nombre': [
                    'ejecutado']
                  }}],
            chart_options =
              {
                  'title': {'text': 'Gastos ejecutados: %s %s' % (municipio, year,)},
                  'options3d': { 'enabled': 'true',  'alpha': '45', 'beta': '0' },
                  'plotOptions': { 'pie': { 'dataLabels': { 'enabled': False }, 'showInLegend': True, 'depth': 35}},
                  'tooltip': { 'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>' },
              })

    # tabla: get total and percent
    total = source.aggregate(total=Sum('ejecutado'))['total']
    for row in source:
        row['percent'] = round(row['ejecutado'] / total * 100, 0)

    # tabla: get gastos por año
    if municipio:
        source_cuadro = GastoDetalle.objects.filter(gasto__municipio__slug=municipio)
    else:
        source_cuadro = GastoDetalle.objects.all()
    porano_table = {}
    ys = source_cuadro.order_by('subsubtipogasto__origen__nombre').values('subsubtipogasto__origen__nombre').distinct()
    for y in ys:
        label = y['subsubtipogasto__origen__nombre']
        porano_table[label] = {}
        for ayear in year_list:
            periodo = Anio.objects.get(anio=ayear).periodo
            quesumar = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'
            value = source_cuadro.filter(gasto__year=ayear, gasto__periodo=periodo, subsubtipogasto__origen__nombre=label).aggregate(total=Sum(quesumar))['total']
            porano_table[label][ayear] = value if value else ''
        if municipio and year:
            periodo = PERIODO_FINAL
            quesumar = 'ejecutado'
            value = GastoDetalle.objects.filter(gasto__year=year, gasto__periodo=periodo, subsubtipogasto__origen__nombre=label, \
                    gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, gasto__municipio__clase__anio=year).\
                    aggregate(total=Sum(quesumar))['total']
            if value:
                value = value / mi_clase_count
            porano_table[label]['extra'] = value if value else '...'

    if portada:
        charts =  (ejecutado, )
    elif municipio:
        charts =  (ejecutado, ogm_comparativo_anios_column, ogm_comparativo2_column, ogm_comparativo3_column, ogm_tipo_column, asignado_barra, barra, )
    else:
        charts =  (ejecutado, ogm_tipo_column, asignado_barra, barra, )

    return {'charts': charts, \
            'clasificacion': mi_clase, 'municipio': municipio, 'anio': year, 'porano': porano_table, 'totales': source, \
            'year_list': year_list, 'municipio_list': municipio_list}
