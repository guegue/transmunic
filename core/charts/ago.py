# -*- coding: utf-8 -*-

import json
from operator import itemgetter

from django.conf import settings
from django.db import connection
from django.db.models import Sum
from django.shortcuts import render

from chartit import Chart, RawDataPool

from core.models import (Anio, IngresoDetalle, GastoDetalle,
                         Gasto, Municipio, TipoIngreso, TipoGasto)
from core.models import (PERIODO_INICIAL, PERIODO_ACTUALIZADO,
                         PERIODO_FINAL)
from core.tools import (getYears, getPeriods, dictfetchall,
                        glue, superglue, xnumber,
                        percentage)
from core.history import (historial_gastos_corrientes,
                          historial_ingresos_corrientes)
from core.graphics import graphChart
from core.charts.misc import getVar
from lugar.models import ClasificacionMunicAno

colorscheme = settings.CHARTS_COLORSCHEME
colors_array = settings.COLORS_ARRAY
chart_options = settings.CHART_OPTIONS


def ago_chart(request, municipio=None, year=None, portada=False):

    municipio_list = Municipio.objects.all()
    municipio = getVar('municipio', request)
    year_list = getYears(Gasto)
    periodo_list = getPeriods(Gasto)
    year = getVar('year', request)
    if not year:
        year = year_list[-1]

    # obtiene último periodo del año que se quiere ver
    year_data = Anio.objects.get(anio=year)
    periodo = year_data.periodo
    quesumar = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'
    datacol = 'inicial_asignado' if periodo == PERIODO_INICIAL else 'ejecutado'

    # obtiene codigo de tipo gasto de 'mapping' fallback a valor por defecto definido en models
    TipoIngreso.TRANSFERENCIAS_CORRIENTES = year_data.mapping.get(
        'transferencias_corrientes', TipoIngreso.TRANSFERENCIAS_CORRIENTES)
    # recolectando los codigos de transferencias de corrientes de cada año
    codigos_trans_corriente = [amap['transferencias_corrientes'] for amap in Anio.objects.all().
                      values_list('mapping', flat=True).distinct()]
    municipio_id = None

    if municipio:
        municipio_row = Municipio.objects.get(slug=municipio)
        municipio_id = municipio_row.id
        municipio_nombre = municipio_row.nombre
        porclasep = None

        source_inicial = IngresoDetalle.objects.filter(
            ingreso__periodo=PERIODO_INICIAL,
            ingreso__municipio__slug=municipio,
            tipoingreso__clasificacion=TipoIngreso.CORRIENTE)\
            .exclude(tipoingreso=TipoIngreso.TRANSFERENCIAS_CORRIENTES)\
            .values('ingreso__anio')\
            .order_by('ingreso__anio')\
            .annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_final = IngresoDetalle.objects.filter(
            ingreso__periodo=periodo,
            ingreso__municipio__slug=municipio,
            tipoingreso__clasificacion=TipoIngreso.CORRIENTE)\
            .exclude(tipoingreso=TipoIngreso.TRANSFERENCIAS_CORRIENTES)\
            .values('ingreso__anio')\
            .order_by('ingreso__anio')\
            .annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        # obtiene valores para este año de las listas
        try:
            asignado = (item for item in source_inicial if item["ingreso__anio"] == int(
                year)).next()['asignado']
        except StopIteration:
            asignado = 0
        try:
            ejecutado = (item for item in source_final if item["ingreso__anio"] == int(year)).next()[
                'ejecutado']
        except StopIteration:
            ejecutado = 0

        # obtiene datos comparativo de ingresos de todos los años
        inicial = list(IngresoDetalle.objects.
                       filter(ingreso__municipio__slug=municipio,
                              ingreso__periodo=PERIODO_INICIAL,
                              tipoingreso__clasificacion=TipoIngreso.CORRIENTE).
                       exclude(tipoingreso__in=codigos_trans_corriente).
                       values('ingreso__anio',
                              'ingreso__periodo').
                       annotate(asignado=Sum('asignado')).
                       order_by())
        final = list(IngresoDetalle.objects.
                     filter(ingreso__municipio__slug=municipio,
                            ingreso__periodo=PERIODO_FINAL,
                            tipoingreso__clasificacion=TipoIngreso.CORRIENTE).
                     exclude(tipoingreso__in=codigos_trans_corriente).
                     values('ingreso__anio', 'ingreso__periodo').
                     annotate(ejecutado=Sum('ejecutado')).
                     order_by())
        anual2 = glue(inicial=inicial,
                      final=final,
                      key='ingreso__anio')

        # obtiene datos comparativo de gastos de todos los años
        inicialg = list(GastoDetalle.objects.
                        filter(gasto__municipio__slug=municipio,
                               gasto__periodo=PERIODO_INICIAL,
                               subsubtipogasto__clasificacion=TipoGasto.CORRIENTE).
                        values('gasto__anio',
                               'gasto__periodo').
                        annotate(asignado=Sum('asignado')).
                        order_by())
        finalg = list(GastoDetalle.objects.
                      filter(gasto__municipio__slug=municipio,
                             gasto__periodo=PERIODO_FINAL,
                             subsubtipogasto__clasificacion=TipoGasto.CORRIENTE).
                      values('gasto__anio',
                             'gasto__periodo').
                      annotate(ejecutado=Sum('ejecutado')).
                      order_by())

        anual2g = glue(inicial=inicialg,
                       final=finalg,
                       key='gasto__anio')

        # obtiene datos de gastos en ditintos rubros
        rubrosg_inicial = GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio,
                                                      gasto__periodo=PERIODO_INICIAL,
                                                      subsubtipogasto__clasificacion=TipoGasto.CORRIENTE, ). \
            values('tipogasto', 'tipogasto__nombre').order_by(
            'tipogasto__codigo').annotate(inicial_asignado=Sum('asignado'))
        rubrosg_actualizado = GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio,
                                                          gasto__periodo=PERIODO_ACTUALIZADO,
                                                          subsubtipogasto__clasificacion=TipoGasto.CORRIENTE, ). \
            values('tipogasto', 'tipogasto__nombre').order_by('tipogasto__codigo').annotate(
            actualizado_asignado=Sum('asignado'), actualizado_ejecutado=Sum('ejecutado'))
        rubrosg_final = GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio,
                                                    gasto__periodo=PERIODO_FINAL,
                                                    subsubtipogasto__clasificacion=TipoGasto.CORRIENTE, ). \
            values('tipogasto', 'tipogasto__nombre').order_by('tipogasto__codigo').annotate(
            final_ejecutado=Sum('ejecutado'), final_asignado=Sum('asignado'))
        rubrosg_periodo = GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio,
                                                      gasto__periodo=periodo,
                                                      subsubtipogasto__clasificacion=TipoGasto.CORRIENTE, ). \
            values('tipogasto', 'tipogasto__nombre').order_by('tipogasto__codigo').annotate(
            ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        rubrosg = superglue(data=(rubrosg_inicial, rubrosg_final,
                                  rubrosg_actualizado, rubrosg_periodo), key='tipogasto')

        # obtiene datos de ingresos en ditintos rubros de corriente (clasificacion 0)
        rubros_inicial = IngresoDetalle.objects. \
            filter(ingreso__anio=year,
                   ingreso__municipio__slug=municipio,
                   ingreso__periodo=PERIODO_INICIAL,
                   tipoingreso__clasificacion=TipoIngreso.CORRIENTE). \
            exclude(tipoingreso=TipoIngreso.TRANSFERENCIAS_CORRIENTES). \
            values('tipoingreso',
                   'tipoingreso__nombre'). \
            order_by('tipoingreso__codigo'). \
            annotate(inicial_asignado=Sum('asignado'))

        rubros_actualizado = IngresoDetalle.objects. \
            filter(ingreso__anio=year,
                   ingreso__municipio__slug=municipio,
                   ingreso__periodo=PERIODO_ACTUALIZADO,
                   tipoingreso__clasificacion=TipoIngreso.CORRIENTE). \
            exclude(tipoingreso=TipoIngreso.TRANSFERENCIAS_CORRIENTES). \
            values('tipoingreso',
                   'tipoingreso__nombre'). \
            order_by('tipoingreso__codigo'). \
            annotate(actualizado_asignado=Sum('asignado'),
                     actualizado_ejecutado=Sum('ejecutado'))
        rubros_final = IngresoDetalle.objects. \
            filter(ingreso__anio=year,
                   ingreso__municipio__slug=municipio,
                   ingreso__periodo=PERIODO_FINAL,
                   tipoingreso__clasificacion=TipoIngreso.CORRIENTE). \
            exclude(tipoingreso=TipoIngreso.TRANSFERENCIAS_CORRIENTES). \
            values('tipoingreso',
                   'tipoingreso__nombre'). \
            order_by('tipoingreso__codigo'). \
            annotate(final_asignado=Sum('asignado'),
                     final_ejecutado=Sum('ejecutado'))
        rubros_periodo = IngresoDetalle.objects. \
            filter(ingreso__anio=year,
                   ingreso__municipio__slug=municipio,
                   ingreso__periodo=periodo,
                   tipoingreso__clasificacion=TipoIngreso.CORRIENTE). \
            exclude(tipoingreso=TipoIngreso.TRANSFERENCIAS_CORRIENTES). \
            values('tipoingreso',
                   'tipoingreso__nombre'). \
            order_by('tipoingreso__codigo'). \
            annotate(asignado=Sum('asignado'),
                     ejecutado=Sum('ejecutado'))
        rubros = superglue(data=(rubros_inicial, rubros_final,
                                 rubros_actualizado, rubros_periodo), key='tipoingreso')

        # obtiene clase y contador (otros en misma clase) para este año
        mi_clase = ClasificacionMunicAno.objects.get(municipio__id=municipio_id, anio=year)
        # mi_clase_count = ClasificacionMunicAno.objects.filter(
        #    clasificacion__clasificacion=mi_clase.clasificacion, anio=year).count()
        # obtiene clase y contador (otros en misma clase) para todos los años
        mi_clase_anios = list(ClasificacionMunicAno.objects.filter(
            municipio__slug=municipio).values('anio', 'clasificacion__clasificacion').annotate())
        mi_clase_anios_count = {}
        for aclase in mi_clase_anios:
            mi_clase_anios_count[aclase['anio']] = ClasificacionMunicAno.objects.filter(
                clasificacion__clasificacion=aclase['clasificacion__clasificacion'], anio=aclase['anio']).count()

        # grafico de ejecutado y asignado a nivel nacional (distintas clases) porcentage
        with open("core/charts/ago_otros.sql", "r") as query_file:
            sql_tpl = query_file.read()

        sql = sql_tpl.format(quesumar="asignado", year=year, periodo=PERIODO_INICIAL, tipoingreso=TipoIngreso.CORRIENTE,
                             notipoingreso=TipoIngreso.TRANSFERENCIAS_CORRIENTES, mi_clase=mi_clase.clasificacion_id)
        cursor = connection.cursor()
        cursor.execute(sql)
        inicial = dictfetchall(cursor)
        sql = sql_tpl.format(quesumar="ejecutado", year=year, periodo=periodo, tipoingreso=TipoIngreso.CORRIENTE,
                             notipoingreso=TipoIngreso.TRANSFERENCIAS_CORRIENTES, mi_clase=mi_clase.clasificacion_id)
        cursor = connection.cursor()
        cursor.execute(sql)
        final = dictfetchall(cursor)
        sql = sql_tpl.format(quesumar="asignado", year=year, periodo=PERIODO_ACTUALIZADO,
                             tipoingreso=TipoIngreso.CORRIENTE,
                             notipoingreso=TipoIngreso.TRANSFERENCIAS_CORRIENTES, mi_clase=mi_clase.clasificacion_id)
        cursor = connection.cursor()
        cursor.execute(sql)
        actualizado = dictfetchall(cursor)
        otros = glue(inicial, final, 'nombre', actualizado=actualizado)
        sort_key = "{}".format(quesumar)
        otros = sorted(otros, key=itemgetter(sort_key), reverse=True)

        with open("core/charts/ago_municipio.sql", "r") as query_file:
            sql_tpl = query_file.read()
        sql = sql_tpl.format(municipio=municipio, year_list=year_list)
        cursor = connection.cursor()
        cursor.execute(sql)
        source = dictfetchall(cursor)

    else:
        #
        # no municipio
        #
        otros = None
        mi_clase = None
        municipio_row = ''
        municipio = ''

        # obtiene datos comparativo de ingresos de todos los años
        inicial = list(IngresoDetalle.objects.
                       filter(ingreso__periodo=PERIODO_INICIAL,
                              tipoingreso__clasificacion=TipoIngreso.CORRIENTE).
                       exclude(tipoingreso__in=codigos_trans_corriente).
                       values('ingreso__anio',
                              'ingreso__periodo').
                       order_by('ingreso__anio',
                                'ingreso__periodo').
                       annotate(asignado=Sum('asignado')))
        final = list(IngresoDetalle.objects.
                     filter(ingreso__periodo=PERIODO_FINAL,
                            tipoingreso__clasificacion=TipoIngreso.CORRIENTE).
                     exclude(tipoingreso__in=codigos_trans_corriente).
                     values('ingreso__anio',
                            'ingreso__periodo').
                     order_by('ingreso__anio',
                              'ingreso__periodo').
                     annotate(ejecutado=Sum('ejecutado')))
        anual2 = glue(inicial=inicial,
                      final=final,
                      key='ingreso__anio')

        # obtiene datos comparativo de gastos de todos los años
        inicialg = list(GastoDetalle.objects.
                        filter(gasto__periodo=PERIODO_INICIAL,
                               subsubtipogasto__clasificacion=TipoGasto.CORRIENTE).
                        values('gasto__anio',
                               'gasto__periodo').
                        order_by('gasto__anio',
                                 'gasto__periodo').
                        annotate(asignado=Sum('asignado')))
        finalg = list(GastoDetalle.objects.
                      filter(gasto__periodo=PERIODO_FINAL,
                             subsubtipogasto__clasificacion=TipoGasto.CORRIENTE).
                      values('gasto__anio',
                             'gasto__periodo').
                      order_by('gasto__anio',
                               'gasto__periodo').
                      annotate(ejecutado=Sum('ejecutado')))

        anual2g = glue(inicial=inicialg,
                       final=finalg,
                       key='gasto__anio')

        # obtiene datos de gastos en ditintos rubros
        rubrosg_inicial = GastoDetalle.objects. \
            filter(gasto__anio=year,
                   gasto__periodo=PERIODO_INICIAL,
                   subsubtipogasto__clasificacion=TipoGasto.CORRIENTE). \
            values('tipogasto',
                   'tipogasto__nombre'). \
            order_by('tipogasto__codigo'). \
            annotate(inicial_asignado=Sum('asignado'))
        rubrosg_actualizado = GastoDetalle.objects. \
            filter(gasto__anio=year,
                   gasto__periodo=PERIODO_ACTUALIZADO,
                   subsubtipogasto__clasificacion=TipoGasto.CORRIENTE). \
            values('tipogasto',
                   'tipogasto__nombre'). \
            order_by('tipogasto__codigo'). \
            annotate(actualizado_asignado=Sum('asignado'),
                     actualizado_ejecutado=Sum('ejecutado'))
        rubrosg_final = GastoDetalle.objects. \
            filter(gasto__anio=year,
                   gasto__periodo=PERIODO_FINAL,
                   subsubtipogasto__clasificacion=TipoGasto.CORRIENTE). \
            values('tipogasto',
                   'tipogasto__nombre'). \
            order_by('tipogasto__codigo'). \
            annotate(final_asignado=Sum('asignado'),
                     final_ejecutado=Sum('ejecutado'))
        rubrosg_periodo = GastoDetalle.objects. \
            filter(gasto__anio=year,
                   gasto__periodo=periodo,
                   subsubtipogasto__clasificacion=TipoGasto.CORRIENTE). \
            values('tipogasto',
                   'tipogasto__nombre'). \
            order_by('tipogasto__codigo'). \
            annotate(ejecutado=Sum('ejecutado'))
        rubrosg = superglue(data=(rubrosg_inicial,
                                  rubrosg_final,
                                  rubrosg_actualizado,
                                  rubrosg_periodo),
                            key='tipogasto')

        # obtiene datos de ingresos en ditintos rubros
        rubros_inicial = IngresoDetalle.objects. \
            filter(ingreso__anio=year,
                   ingreso__periodo=PERIODO_INICIAL,
                   tipoingreso__clasificacion=TipoIngreso.CORRIENTE). \
            exclude(tipoingreso=TipoIngreso.TRANSFERENCIAS_CORRIENTES). \
            values('tipoingreso',
                   'tipoingreso__nombre'). \
            order_by('tipoingreso__codigo'). \
            annotate(inicial_asignado=Sum('asignado'))
        rubros_actualizado = IngresoDetalle.objects. \
            filter(ingreso__anio=year,
                   ingreso__periodo=PERIODO_ACTUALIZADO,
                   tipoingreso__clasificacion=TipoIngreso.CORRIENTE). \
            exclude(tipoingreso=TipoIngreso.TRANSFERENCIAS_CORRIENTES). \
            values('tipoingreso',
                   'tipoingreso__nombre'). \
            order_by('tipoingreso__codigo'). \
            annotate(actualizado_asignado=Sum('asignado'),
                     actualizado_ejecutado=Sum('ejecutado'))
        rubros_final = IngresoDetalle.objects. \
            filter(ingreso__anio=year,
                   ingreso__periodo=PERIODO_FINAL,
                   tipoingreso__clasificacion=TipoIngreso.CORRIENTE). \
            exclude(tipoingreso=TipoIngreso.TRANSFERENCIAS_CORRIENTES). \
            values('tipoingreso',
                   'tipoingreso__nombre'). \
            order_by('tipoingreso__codigo'). \
            annotate(final_asignado=Sum('asignado'),
                     final_ejecutado=Sum('ejecutado'))
        rubros_periodo = IngresoDetalle.objects. \
            filter(ingreso__anio=year,
                   ingreso__periodo=periodo,
                   tipoingreso__clasificacion=TipoIngreso.CORRIENTE). \
            exclude(tipoingreso=TipoIngreso.TRANSFERENCIAS_CORRIENTES). \
            values('tipoingreso',
                   'tipoingreso__nombre'). \
            order_by('tipoingreso__codigo'). \
            annotate(asignado=Sum('asignado'),
                     ejecutado=Sum('ejecutado'))

        rubros = superglue(data=(rubros_inicial,
                                 rubros_final,
                                 rubros_actualizado,
                                 rubros_periodo),
                           key='tipoingreso')

        source_inicial = IngresoDetalle.objects. \
            filter(ingreso__periodo=PERIODO_INICIAL,
                   tipoingreso__clasificacion=TipoGasto.CORRIENTE). \
            exclude(tipoingreso=TipoIngreso.TRANSFERENCIAS_CORRIENTES). \
            values('ingreso__anio'). \
            order_by('ingreso__anio'). \
            annotate(ejecutado=Sum('ejecutado'),
                     asignado=Sum('asignado'))
        source_final = IngresoDetalle.objects. \
            filter(ingreso__periodo=periodo,
                   tipoingreso__clasificacion=TipoGasto.CORRIENTE). \
            exclude(tipoingreso=TipoIngreso.TRANSFERENCIAS_CORRIENTES). \
            values('ingreso__anio'). \
            order_by('ingreso__anio'). \
            annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

        # obtiene valores para este año de las listas
        try:
            asignado = (item for item in source_inicial if item["ingreso__anio"] == int(
                year)).next()['asignado']
        except StopIteration:
            asignado = 0
        try:
            ejecutado = (item for item in source_final if item["ingreso__anio"] == int(
                year)).next()['ejecutado']
        except StopIteration:
            ejecutado = 0

        # grafico de ejecutado y asignado a nivel nacional (distintas clases) porcentage
        with open("core/charts/ago_porclasep.sql", "r") as query_file:
            sql_tpl = query_file.read()

        sql = sql_tpl.format(quesumar="asignado",
                             year=year,
                             periodo=PERIODO_INICIAL,
                             tipoingreso=TipoIngreso.CORRIENTE,
                             notipoingreso=TipoIngreso.TRANSFERENCIAS_CORRIENTES)
        cursor = connection.cursor()
        cursor.execute(sql)
        inicial = dictfetchall(cursor)
        sql = sql_tpl.format(quesumar="ejecutado",
                             year=year, periodo=periodo,
                             tipoingreso=TipoIngreso.CORRIENTE,
                             notipoingreso=TipoIngreso.TRANSFERENCIAS_CORRIENTES)
        cursor = connection.cursor()
        cursor.execute(sql)
        final = dictfetchall(cursor)
        sql = sql_tpl.format(quesumar="asignado",
                             year=year,
                             periodo=PERIODO_ACTUALIZADO,
                             tipoingreso=TipoIngreso.CORRIENTE,
                             notipoingreso=TipoIngreso.TRANSFERENCIAS_CORRIENTES)
        cursor = connection.cursor()
        cursor.execute(sql)
        actualizado = dictfetchall(cursor)
        porclasep = glue(inicial, final, 'clasificacion', actualizado=actualizado)

        with open("core/charts/ago.sql", "r") as query_file:
            sql_tpl = query_file.read()
        sql = sql_tpl.format(municipio=municipio, year_list=year_list)
        cursor = connection.cursor()
        cursor.execute(sql)
        source = dictfetchall(cursor)

    # calcular el porcentaje de los rubros
    for row in rubros:
        row['asignado_porcentaje'] = percentage(row['asignado'], asignado)
        row['ejecutado_porcentaje'] = percentage(row['ejecutado'], ejecutado)

    # calcular el porcentaje de los rubrosg
    for row in rubrosg:
        row['asignado_porcentaje'] = percentage(row['inicial_asignado'], asignado, 2)
        row['ejecutado_porcentaje'] = percentage(row['ejecutado'], ejecutado, 2)

    for row in anual2g:
        if row['asignado']:
            row['ejecutado_porcentaje'] = percentage(row['ejecutado'], row['asignado'])

    data = RawDataPool(
        series=[
            {
                'options': {'source': source},
                'terms': [
                    'anio',
                    'ejecutado',
                    'asignado',
                ]
            }
        ]
    )

    data_ingreso = RawDataPool(
        series=[
            {
                'options': {'source': rubros},
                'terms': [
                    'tipoingreso__nombre',
                    datacol,
                ]}
        ])
    pie = Chart(
        datasource=data_ingreso,
        series_options=[{
            'options': {
                'type': 'pie'
            },
            'terms': {
                'tipoingreso__nombre': [datacol]
            }
        }],
        chart_options=chart_options,
    )

    bar = Chart(
        datasource=data_ingreso,
        series_options=[
            {
                'options': {
                    'type': 'column',
                    'colorByPoint': True
                },
                'terms': {
                    'tipoingreso__nombre': [datacol]
                }
            }],
        chart_options=chart_options)

    data_gasto = RawDataPool(
        series=[
            {
                'options': {'source': rubrosg},
                'terms': ['tipogasto__nombre', datacol]
            }
        ])

    pie2 = Chart(
        datasource=data_gasto,
        series_options=[
            {
                'options': {'type': 'pie'},
                'terms': {'tipogasto__nombre': [datacol]}
            }],
        chart_options=chart_options)

    bar2 = Chart(
        datasource=data_gasto,
        series_options=[
            {
                'options': {
                    'type': 'column',
                    'colorByPoint': True,
                },
                'terms': {'tipogasto__nombre': [datacol]}
            }],
        chart_options=chart_options)

    # fusionando anuales y anualesg
    anuales = []
    for i in range(len(anual2)):
        ago = anual2[i].get('asignado', 0) - anual2g[i].get('asignado', 0)
        anuales.append({
            'anio': anual2[i].get('ingreso__anio', 0),
            'total_ingreso': anual2[i].get('asignado', 0),
            'total_gasto': anual2g[i].get('asignado', 0),
            'diferencia': ago,
            'diferencia_porcentaje': percentage(ago, anual2[i].get('asignado'))
        })

    historico_ingreso = historial_ingresos_corrientes(periodo_list, year,
                                                      TipoIngreso.TRANSFERENCIAS_CORRIENTES,
                                                      municipio_id)
    historico_gasto = historial_gastos_corrientes(periodo_list, year,
                                                  municipio_id)
    # FIXME BS
    porclase = None

    reporte = request.POST.get("reporte", "")
    if "excel" in request.POST.keys() and reporte:
        from core.utils import obtener_excel_response
        data = {
            'charts': (bar,),
            'indicator_name': "Dependencia para asumir gastos corrientes",
            'source': source,
            'mi_clase': mi_clase,
            'municipio': municipio_row,
            'year': year,
            'ejecutado': ejecutado,
            'asignado': asignado,
            'year_list': year_list,
            'municipio_list': municipio_list,
            'anuales': anuales,
            'porclase': porclase,
            'porclasep': porclasep,
            'rubros': rubros,
            'rubrosg': rubrosg,
            'mostraren': "porcentaje",
            'periodo_list': periodo_list,
            'historico_ingreso': historico_ingreso,
            'historico_gasto': historico_gasto,
            'otros': otros}
        return obtener_excel_response(reporte=reporte, data=data)

    bubble_data_ingreso = aci_bubbletree_data_ingreso(municipio, year, portada)
    bubble_data_gasto = aci_bubbletree_data_gasto(municipio, year, portada)

    bar_horizontal = None
    # bar horizontal
    if otros:
        parameters = {
            'data': otros,
            'field1': 'nombre',
            'field2': quesumar,
            'typechart': 'bar',
            'title': "Ranking de Municipios Categoría '{}'".
                format(mi_clase.clasificacion),
            'labelX_axis': 'Municipio',
            'labelY_axis': 'Recaudación por habitante en córdobas corrientes',
            'pointFormat': '<span>' + quesumar + '</span>:<b>{point.y:.2f}%</b>',
        }
        bar_horizontal = graphChart(parameters)
    elif porclasep:
        if periodo == 'I':
            periodo_nombre = 'Inicial'
        elif periodo == 'A':
            periodo_nombre = 'Intermedio'
        else:
            periodo_nombre = 'Cierre'
        titulo = 'Dependencia para asumir gastos ' \
                 'corrientes {year} periodo {periodo}'.format(year=year,
                                                              periodo=periodo_nombre)
        parameters = {
            'data': porclasep,
            'field1': 'clasificacion',
            'field2': '{}_porcentaje'.format(quesumar),
            'typechart': 'column',
            'title': titulo,
            'labelX_axis': 'Grupos',
            'labelY_axis': 'Porcentaje',
            'interval': 10,
            'pointFormat': '<span>{series.name}</span>:<b>{point.y:.2f}%</b>',
        }
        bar_horizontal = graphChart(parameters)

    template_name = 'variance_analysis.html'
    context = {
        'charts': (pie, bar, pie2, bar2, bar_horizontal,),
        'source': source,
        'indicator_name': "Dependencia para asumir gastos corrientes",
        'indicator_subtitle': "Ingresos corrientes propios por rubro",
        'indicator_subtitle2': "Gastos corrientes totales por rubro",
        'rankin_name': "Dependencia para asumir gastos corrientes con ingresos propios",
        'indicator_description': """Mide el grado de dependencia que tiene el municipio 
                para cubrir los gastos de operación o de funcionamiento con sus propios 
                recursos corrientes, sin depender de recursos externos al municipio. 
                Un resultado negativo significa que es dependiente y si es positivo es auto sostenible.
                 """,
        'bubble_data_1': bubble_data_ingreso,
        'bubble_data_2': bubble_data_gasto,
        'mi_clase': mi_clase,
        'municipio': municipio_row,
        'year': year,
        'ejecutado': ejecutado,
        'asignado': asignado,
        'year_list': year_list,
        'municipio_list': municipio_list,
        'anuales': anuales,
        'history': zip(anual2, anual2g),
        'porclase': porclase,
        'porclasep': porclasep,
        'rubros': rubros,
        'periodo_list': periodo_list,
        'historico_ingreso': historico_ingreso,
        'historico_gasto': historico_gasto,
        'rubrosg': rubrosg,
        'mostraren': "porcentaje",
        'otros': otros
    }
    return render(request, template_name, context)


def aci_bubbletree_data_ingreso(
        municipio=None, year=None, portada=False, total=0):
    year_list = getYears(Gasto)
    periodo = Anio.objects.get(anio=year).periodo
    if not year:
        year = year_list[-1]
    amount_column = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'

    if municipio:
        tipos = IngresoDetalle.objects.filter(
            ingreso__anio=year,
            ingreso__municipio__slug=municipio,
            ingreso__periodo=periodo,
            tipoingreso__clasificacion=TipoIngreso.CORRIENTE) \
            .exclude(tipoingreso=TipoIngreso.TRANSFERENCIAS_CORRIENTES) \
            .values('tipoingreso', 'tipoingreso__nombre', 'tipoingreso__shortname') \
            .order_by('tipoingreso__codigo') \
            .annotate(amount=Sum(amount_column))
        amount = IngresoDetalle.objects.filter(
            ingreso__anio=year,
            ingreso__municipio__slug=municipio,
            ingreso__periodo=periodo,
            tipoingreso__clasificacion=TipoIngreso.CORRIENTE) \
            .exclude(tipoingreso=TipoIngreso.TRANSFERENCIAS_CORRIENTES) \
            .aggregate(total=Sum(amount_column))
    else:
        tipos = IngresoDetalle.objects.filter(
            ingreso__anio=year,
            ingreso__periodo=periodo,
            tipoingreso__clasificacion=TipoIngreso.CORRIENTE) \
            .exclude(tipoingreso=TipoIngreso.TRANSFERENCIAS_CORRIENTES) \
            .values('tipoingreso', 'tipoingreso__nombre', 'tipoingreso__shortname') \
            .order_by('tipoingreso__codigo') \
            .annotate(amount=Sum(amount_column))
        amount = IngresoDetalle.objects.filter(
            ingreso__anio=year,
            ingreso__periodo=periodo,
            tipoingreso__clasificacion=TipoIngreso.CORRIENTE) \
            .exclude(tipoingreso=TipoIngreso.TRANSFERENCIAS_CORRIENTES) \
            .aggregate(total=Sum(amount_column))

    data = {
        'label': "Ingreso Corriente",
        'amount': round(xnumber(amount['total']) / 1000000,
                        2)
    }
    children = []
    for idx, child in enumerate(tipos):
        if municipio:
            subtipos = IngresoDetalle.objects.filter(
                ingreso__anio=year,
                ingreso__municipio__slug=municipio,
                ingreso__periodo=periodo,
                tipoingreso__codigo=child['tipoingreso']) \
                .values(
                'subtipoingreso', 'subtipoingreso__nombre',
                'subtipoingreso__shortname') \
                .order_by('subtipoingreso__codigo') \
                .annotate(amount=Sum(amount_column))
        else:
            subtipos = IngresoDetalle.objects.filter(
                ingreso__anio=year,
                ingreso__periodo=periodo,
                tipoingreso__codigo=child['tipoingreso']) \
                .values(
                'subtipoingreso', 'subtipoingreso__nombre',
                'subtipoingreso__shortname') \
                .order_by('subtipoingreso__codigo') \
                .annotate(amount=Sum(amount_column))
        grandchildren = []
        for ix, grandchild in enumerate(subtipos):
            if grandchild['subtipoingreso__shortname']:
                label = grandchild['subtipoingreso__shortname']
            else:
                label = grandchild['subtipoingreso__nombre']
            grandchild_data = {
                'id': '{}.{}'.format(idx, ix),
                'name': '{}.{}'.format(idx, ix),
                'label': label,
                'amount': round(xnumber(grandchild['amount']) / 1000000,
                                2)
            }
            grandchildren.append(grandchild_data)
        if child['tipoingreso__shortname']:
            label = child['tipoingreso__shortname']
        else:
            label = child['tipoingreso__nombre']
        child_data = {
            'taxonomy': "income",
            'id': idx,
            'name': idx,
            'label': label,
            'amount': round(xnumber(child['amount']) / 1000000,
                            2),
        }
        if grandchildren.__len__() > 3:
            child_data['children'] = grandchildren
        children.append(child_data)
    data['children'] = children
    return json.dumps(data)


def aci_bubbletree_data_gasto(
        municipio=None, year=None, portada=False, total=0):
    year_list = getYears(Gasto)
    periodo = Anio.objects.get(anio=year).periodo
    if not year:
        year = year_list[-1]
    amount_column = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'
    if municipio:
        amount = GastoDetalle.objects.filter(
            gasto__anio=year,
            gasto__municipio__slug=municipio,
            gasto__periodo=periodo,
            subsubtipogasto__clasificacion=TipoGasto.CORRIENTE) \
            .aggregate(total=Sum(amount_column))
        tipos = GastoDetalle.objects.filter(
            gasto__anio=year,
            gasto__municipio__slug=municipio,
            gasto__periodo=periodo,
            subsubtipogasto__clasificacion=TipoGasto.CORRIENTE) \
            .values('tipogasto', 'tipogasto__nombre', 'tipogasto__shortname') \
            .order_by('tipogasto__codigo') \
            .annotate(amount=Sum(amount_column))
    else:
        amount = GastoDetalle.objects.filter(
            gasto__anio=year,
            gasto__periodo=periodo,
            subsubtipogasto__clasificacion=TipoGasto.CORRIENTE) \
            .aggregate(total=Sum(amount_column))
        tipos = GastoDetalle.objects.filter(
            gasto__anio=year,
            gasto__periodo=periodo,
            subsubtipogasto__clasificacion=TipoGasto.CORRIENTE) \
            .values('tipogasto', 'tipogasto__nombre', 'tipogasto__shortname') \
            .order_by('tipogasto__codigo') \
            .annotate(amount=Sum(amount_column))
    data = {
        'label': "Gasto Corriente",
        'amount': round(xnumber(amount['total']) / 1000000,
                        2)
    }
    children = []
    for idx, child in enumerate(tipos):
        if municipio:
            subtipos = GastoDetalle.objects.filter(
                gasto__anio=year,
                gasto__municipio__slug=municipio,
                gasto__periodo=periodo,
                subsubtipogasto__codigo=child['tipogasto']) \
                .values('subtipogasto', 'subtipogasto__nombre', 'subtipogasto__shortname') \
                .order_by('subtipogasto__codigo') \
                .annotate(amount=Sum(amount_column))
        else:
            subtipos = GastoDetalle.objects.filter(
                gasto__anio=year,
                gasto__periodo=periodo,
                subsubtipogasto__codigo=child['tipogasto']) \
                .values('subtipogasto', 'subtipogasto__nombre', 'subtipogasto__shortname') \
                .order_by('subtipogasto__codigo') \
                .annotate(amount=Sum(amount_column))
        grandchildren = []
        for ix, grandchild in enumerate(subtipos):
            if grandchild['subtipogasto__shortname']:
                label = grandchild['subtipogasto__shortname']
            else:
                label = grandchild['subtipogasto__nombre']
            grandchild_data = {
                'id': '{}.{}'.format(idx, ix),
                'name': '{}.{}'.format(idx, ix),
                'label': label,
                'amount': round(xnumber(grandchild['amount']) / 1000000,
                                2)
            }
            grandchildren.append(grandchild_data)
        if child['tipogasto__shortname']:
            label = child['tipogasto__shortname']
        else:
            label = child['tipogasto__nombre']
        child_data = {
            'taxonomy': "expense",
            'id': idx,
            'name': idx,
            'label': label,
            'amount': round(xnumber(child['amount']) / 1000000,
                            2),
            'children': grandchildren
        }
        children.append(child_data)
    data['children'] = children
    return json.dumps(data)
