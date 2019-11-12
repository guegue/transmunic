# -*- coding: utf-8 -*-

import json


from django.db import connection
from django.db.models import Sum
from django.shortcuts import render_to_response, render
from django.template import RequestContext

from chartit import Chart, RawDataPool

from core.models import Anio, IngresoDetalle, GastoDetalle, Gasto, Municipio,\
    ClasificacionMunicAno
from core.models import PERIODO_INICIAL, PERIODO_ACTUALIZADO, PERIODO_FINAL,\
    CLASIFICACION_VERBOSE
from core.tools import getYears, dictfetchall, glue, superglue
from core.charts.misc import getVar
from core.charts.bubble_oim import oim_bubble_chart_data
from core.charts.bubble_ogm import ogm_bubble_chart_data

from transmunic import settings as pma_settings

colorscheme = getattr(
    pma_settings,
    'CHARTS_COLORSCHEME',
    [
        '#2b7ab3',
        '#00a7b2 ',
        '#5A4A42',
        '#D65162',
        '#8B5E3B',
        '#84B73F',
        '#AF907F',
        '#FFE070',
        '#25AAE1'])

chart_options = getattr(
    pma_settings,
    'CHART_OPTIONS',
    {}
)


def ep_chart(request):

    municipio_list = Municipio.objects.all()
    municipio = getVar('municipio', request)
    year_list = getYears(Gasto)
    year = getVar('year', request)
    if not year:
        year = year_list[-2]

    periodo = Anio.objects.get(anio=year).periodo
    quesumar = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'
    datacol = 'inicial_asignado' if periodo == PERIODO_INICIAL else 'ejecutado'
    portada = False

    if municipio:
        municipio_row = Municipio.objects.get(slug=municipio)
        municipio_id = municipio_row.id
        municipio_nombre = municipio_row.nombre
        porclasep = None

        # obtiene clase y contador (otros en misma clase) para este año
        mi_clase = ClasificacionMunicAno.objects.get(municipio__slug=municipio, anio=year)
        mi_clase_count = ClasificacionMunicAno.objects.filter(clasificacion__clasificacion=mi_clase.clasificacion, anio=year).count()
        # obtiene clase y contador (otros en misma clase) para todos los años
        mi_clase_anios = list(ClasificacionMunicAno.objects.filter(municipio__slug=municipio).values('anio', 'clasificacion__clasificacion').annotate())
        mi_clase_anios_count = {}

        for aclase in mi_clase_anios:
            mi_clase_anios_count[aclase['anio']] = ClasificacionMunicAno.objects.filter(clasificacion__clasificacion=aclase['clasificacion__clasificacion'], anio=aclase['anio']).count()

        # obtiene datos de municipios de la misma clase
        with open ("core/charts/ep_otros.sql", "r") as query_file:
            sql_tpl=query_file.read()

        sql = sql_tpl.format(var='ingreso', quesumar1="asignado", quesumar2="ejecutado", mi_clase=mi_clase.clasificacion.id, year=year, periodo_inicial=PERIODO_INICIAL, periodo_final=periodo)
        cursor = connection.cursor()
        cursor.execute(sql)
        ingresos = dictfetchall(cursor)
        sql = sql_tpl.format(var='gasto', quesumar1="asignado", quesumar2="ejecutado", mi_clase=mi_clase.clasificacion.id, year=year, periodo_inicial=PERIODO_INICIAL, periodo_final=periodo)
        cursor = connection.cursor()
        cursor.execute(sql)
        gastos = dictfetchall(cursor)
        otros = glue(ingresos, gastos, 'nombre')

        # obtiene datos de gastos en ditintos rubros
        rubrosg_inicial = GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL,).\
                values('tipogasto__clasificacion',).order_by('tipogasto__clasificacion').annotate(inicial_asignado=Sum('asignado'))
        rubrosg_actualizado = GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio, gasto__periodo=PERIODO_ACTUALIZADO,).\
                values('tipogasto__clasificacion',).order_by('tipogasto__clasificacion').annotate(actualizado_asignado=Sum('asignado'), actualizado_ejecutado=Sum('ejecutado'))
        rubrosg_final = GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio, gasto__periodo=PERIODO_FINAL,).\
                values('tipogasto__clasificacion').order_by('tipogasto__clasificacion').annotate(final_asignado=Sum('asignado'), final_ejecutado=Sum('ejecutado'))
        rubrosg_periodo = GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio, gasto__periodo=periodo,).\
                values('tipogasto__clasificacion').order_by('tipogasto__clasificacion').annotate(asignado=Sum('asignado'), ejecutado=Sum('ejecutado'))
        rubrosg = superglue(data=(rubrosg_inicial, rubrosg_final, rubrosg_actualizado, rubrosg_periodo), key='tipogasto__clasificacion')
        for r in rubrosg:
            r['tipogasto__clasificacion'] = CLASIFICACION_VERBOSE[r['tipogasto__clasificacion']]

        # obtiene datos de ingresos en ditintos rubros de corriente (clasificacion 0)
        rubros_inicial = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_INICIAL,).\
                values('tipoingreso__clasificacion').order_by('tipoingreso__clasificacion').annotate(inicial_asignado=Sum('asignado'))
        rubros_actualizado = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_ACTUALIZADO,).\
                values('tipoingreso__clasificacion').order_by('tipoingreso__clasificacion').annotate(actualizado_asignado=Sum('asignado'), actualizado_ejecutado=Sum('ejecutado'))
        rubros_final = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_FINAL,).\
                values('tipoingreso__clasificacion').order_by('tipoingreso__clasificacion').annotate(final_asignado=Sum('asignado'), final_ejecutado=Sum('ejecutado'))
        rubros_periodo = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__municipio__slug=municipio, ingreso__periodo=periodo,).\
                values('tipoingreso__clasificacion').order_by('tipoingreso__clasificacion').annotate(asignado=Sum('asignado'), ejecutado=Sum('ejecutado'))
        rubros = superglue(data=(rubros_inicial, rubros_final, rubros_actualizado, rubros_periodo), key='tipoingreso__clasificacion')
        for r in rubros:
            r['tipoingreso__clasificacion'] = CLASIFICACION_VERBOSE[r['tipoingreso__clasificacion']]

        # calculo de La Ejecución presupuestaria alcanzó el:
        # FIXME incial_asignado? o asignado (periodo) ? misma pregunta sobre final_ejecutado.
        ep_ingresos = sum(item['inicial_asignado'] for item in rubros_inicial)
        ep_gastos = sum(item['ejecutado'] for item in rubrosg_periodo)
        if ep_ingresos:
            ep = round(ep_gastos / ep_ingresos * 100, 1)
        else:
            ep = 0

        # obtiene datos comparativo de todos los años
        inicial = list(IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_INICIAL,).values('ingreso__anio', 'ingreso__periodo').annotate(asignado=Sum('asignado')))
        final = list(IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_FINAL,).values('ingreso__anio', 'ingreso__periodo').annotate(ejecutado=Sum('ejecutado')))
        anual2 = glue(inicial=inicial, final=final, key='ingreso__anio')

        # obtiene datos comparativo de todos los años
        inicialg = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL,).values('gasto__anio', 'gasto__periodo').annotate(asignado=Sum('asignado')))
        finalg = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_FINAL,).values('gasto__anio', 'gasto__periodo').annotate(ejecutado=Sum('ejecutado')))
        anual2g = glue(inicial=inicialg, final=finalg, key='gasto__anio')

        with open ("core/charts/ep_municipio.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [municipio, municipio, year_list])
    else:
        #
        # no municipio
        #
        otros = None
        mi_clase = None
        municipio_row = ''
        municipio = ''

        # obtiene datos de gastos en ditintos rubros
        rubrosg_inicial = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_INICIAL,).\
                values('tipogasto__clasificacion',).order_by('tipogasto__clasificacion').annotate(inicial_asignado=Sum('asignado'))
        rubrosg_actualizado = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_ACTUALIZADO,).\
                values('tipogasto__clasificacion',).order_by('tipogasto__clasificacion').annotate(actualizado_asignado=Sum('asignado'), actualizado_ejecutado=Sum('ejecutado'))
        rubrosg_final = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_FINAL,).\
                values('tipogasto__clasificacion').order_by('tipogasto__clasificacion').annotate(final_asignado=Sum('asignado'), final_ejecutado=Sum('ejecutado'))
        rubrosg_periodo = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=periodo,).\
                values('tipogasto__clasificacion').order_by('tipogasto__clasificacion').annotate(asignado=Sum('asignado'), ejecutado=Sum('ejecutado'))
        rubrosg = superglue(data=(rubrosg_inicial, rubrosg_final, rubrosg_actualizado, rubrosg_periodo), key='tipogasto__clasificacion')
        for r in rubrosg:
            r['tipogasto__clasificacion'] = CLASIFICACION_VERBOSE[r['tipogasto__clasificacion']]

        # obtiene datos de ingresos en ditintos rubros de corriente (clasificacion 0)
        rubros_inicial = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_INICIAL,).\
                values('tipoingreso__clasificacion').order_by('tipoingreso__clasificacion').annotate(inicial_asignado=Sum('asignado'))
        rubros_actualizado = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_ACTUALIZADO,).\
                values('tipoingreso__clasificacion').order_by('tipoingreso__clasificacion').annotate(actualizado_asignado=Sum('asignado'), actualizado_ejecutado=Sum('ejecutado'))
        rubros_final = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_FINAL,).\
                values('tipoingreso__clasificacion').order_by('tipoingreso__clasificacion').annotate(final_asignado=Sum('asignado'), final_ejecutado=Sum('ejecutado'))
        rubros_periodo = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=periodo,).\
                values('tipoingreso__clasificacion').order_by('tipoingreso__clasificacion').annotate(asignado=Sum('asignado'), ejecutado=Sum('ejecutado'))
        rubros = superglue(data=(rubros_inicial, rubros_final, rubros_actualizado, rubros_periodo), key='tipoingreso__clasificacion')
        for r in rubros:
            r['tipoingreso__clasificacion'] = CLASIFICACION_VERBOSE[r['tipoingreso__clasificacion']]

        # calculo de La Ejecución presupuestaria alcanzó el:
        ep_ingresos = sum(item['asignado'] for item in rubros_inicial)
        ep_gastos = sum(item['ejecutado'] for item in rubrosg_periodo)
        if ep_ingresos == 0: #FIXME: only way to avoid ZeroDivisionError ?
            ep = 0
        else:
            ep = round(ep_gastos / ep_ingresos * 100, 1)

        with open ("core/charts/ep_porclasep.sql", "r") as query_file:
            sql_tpl=query_file.read()


        # the new way... re-haciendo "porclasep"
        sql = sql_tpl.format(var='ingreso', quesumar1="asignado", quesumar2="ejecutado", year=year, periodo_inicial=PERIODO_INICIAL, periodo_final=periodo)
        cursor = connection.cursor()
        cursor.execute(sql)
        ingresos = dictfetchall(cursor)
        sql = sql_tpl.format(var='gasto', quesumar1="asignado", quesumar2="ejecutado", year=year, periodo_inicial=PERIODO_INICIAL, periodo_final=periodo)
        cursor = connection.cursor()
        cursor.execute(sql)
        gastos = dictfetchall(cursor)
        porclasep = glue(ingresos, gastos, 'clasificacion')

        # obtiene datos comparativo de todos los años
        inicial = list(IngresoDetalle.objects.filter(ingreso__periodo=PERIODO_INICIAL,).values('ingreso__anio', 'ingreso__periodo').annotate(asignado=Sum('asignado')))
        final = list(IngresoDetalle.objects.filter(ingreso__periodo=PERIODO_FINAL,).values('ingreso__anio', 'ingreso__periodo').annotate(ejecutado=Sum('ejecutado')))
        anual2 = glue(inicial=inicial, final=final, key='ingreso__anio')

        # obtiene datos comparativo de todos los años
        inicialg = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL,).values('gasto__anio', 'gasto__periodo').annotate(asignado=Sum('asignado')))
        finalg = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL,).values('gasto__anio', 'gasto__periodo').annotate(ejecutado=Sum('ejecutado')))
        anual2g = glue(inicial=inicialg, final=finalg, key='gasto__anio')

        with open ("core/charts/ep.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [year_list])

    data = RawDataPool(
        series=[
            {
                'options': {'source': source},
                'terms': ['anio', 'ejecutado']
            }
        ])

    data_ingreso = RawDataPool(
        series=[
            {
                'options': {'source': rubros},
                'terms': [
                    'tipoingreso__clasificacion',
                    datacol,
                ]
            }
        ])

    pie = Chart(
        datasource=data_ingreso,
        series_options=[
            {
                'options': {'type': 'pie'},
                'terms': {
                    'tipoingreso__clasificacion': [datacol]
                }
            }],
        chart_options=chart_options)

    bar = Chart(
        datasource=data_ingreso,
        series_options=[
            {
                'options': {
                    'type': 'column',
                    'colorByPoint': True
                    },
                'terms': {
                    'tipoingreso__clasificacion': [datacol]
                }
            }],
        chart_options=chart_options)

    data_gasto = RawDataPool(
           series=[
                {
                    'options': {'source': rubrosg},
                    'terms': [
                        'tipogasto__clasificacion',
                        datacol,
                    ]
                }
            ])

    pie2 = Chart(
        datasource=data_gasto,
        series_options=[
            {
                'options': {'type': 'pie'},
                'terms': {'tipogasto__clasificacion': [datacol]}
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
                'terms': {'tipogasto__clasificacion': [datacol]}
            }],
        chart_options=chart_options)

    # FIXME BS
    # asignado = ejecutado = porclase = None
    asignado = ep_ingresos
    ejecutado = ep_gastos
    porclase = None

    bubble_data_ingreso = oim_bubble_chart_data(municipio=municipio, year=year)
    bubble_data_gasto = ogm_bubble_chart_data(municipio=municipio, year=year)

    reporte = request.POST.get("reporte", "")
    if "excel" in request.POST.keys() and reporte:
        from core.utils import obtener_excel_response
        data = {
            'charts': (bar, ),
            'ep': ep, 'mi_clase': mi_clase, 'municipio': municipio_row,
            'year': year, 'ejecutado': ejecutado, 'asignado': asignado,
            'year_list': year_list, 'municipio_list': municipio_list,
            'anuales': anual2, 'anualesg': anual2g, 'porclase': porclase,
            'porclasep': porclasep, 'rubros': rubros, 'rubrosg': rubrosg,
            'otros': otros}
        return obtener_excel_response(reporte=reporte, data=data)

    template_name = 'variance_analysis.html'
    context = {
            'charts': (pie, bar, pie2, bar2),
            'indicator_name': "Ejecución del presupuesto",
            'indicator_description': """Mide la eficiencia del municipio en
                la ejecución del ingreso y el gasto presupuestado inicialmente.
                Es decir, evaluamos que tanto cambio el presupuesto con
                respecto la ejecución versus lo presupuestado y aprobado en los
                procesos de consulta.""",
            'bubble_data_1': bubble_data_ingreso,
            'bubble_data_2': bubble_data_gasto,
            'ep': ep,
            'mi_clase': mi_clase,
            'municipio': municipio_row,
            'year': year,
            'ejecutado': ejecutado,
            'asignado': asignado,
            'year_list': year_list,
            'municipio_list': municipio_list,
            'anuales': anual2,
            'anualesg': anual2g,
            'history': zip(anual2, anual2g),
            'porclase': porclase,
            'porclasep': porclasep,
            'rubros': rubros,
            'rubrosg': rubrosg,
            'otros': otros}
    return render(request, template_name, context)
