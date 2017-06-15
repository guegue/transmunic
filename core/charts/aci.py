# -*- coding: utf-8 -*-

from itertools import chain
from datetime import datetime, time

from django.db import connection
from django.db.models import Q, Sum, Max, Min, Avg, Count
from django.shortcuts import render_to_response
from django.template import RequestContext

from chartit import DataPool, Chart, PivotDataPool, PivotChart, RawDataPool

from core.models import Anio, IngresoDetalle, Ingreso, GastoDetalle, Gasto, Inversion, Proyecto, Municipio, TipoIngreso, TipoGasto, InversionFuente, InversionFuenteDetalle, CatInversion, ClasificacionMunicAno
from core.models import PERIODO_INICIAL, PERIODO_ACTUALIZADO, PERIODO_FINAL, PERIODO_VERBOSE
from core.tools import getYears, dictfetchall, glue, superglue
from core.charts.misc import getVar


def aci_chart(request, municipio=None, year=None, portada=False):

    municipio_list = Municipio.objects.all()
    municipio = getVar('municipio', request)
    year_list = getYears(Gasto)
    year = getVar('year', request)
    if not year:
        year = year_list[-2]

    periodo = Anio.objects.get(anio=year).periodo
    quesumar = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'

    if municipio:
        municipio_row = Municipio.objects.get(slug=municipio)
        municipio_id = municipio_row.id
        municipio_nombre = municipio_row.nombre
        porclasep = None

        source_inicial = IngresoDetalle.objects.filter(ingreso__periodo=PERIODO_INICIAL, \
            ingreso__municipio__slug=municipio, tipoingreso__clasificacion=TipoGasto.CORRIENTE).\
            values('ingreso__anio').order_by('ingreso__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_final = IngresoDetalle.objects.filter(ingreso__periodo=periodo, \
            ingreso__municipio__slug=municipio, tipoingreso__clasificacion=TipoGasto.CORRIENTE).\
            values('ingreso__anio').order_by('ingreso__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        # obtiene valores para este año de las listas
        try:
            asignado = (item for item in source_inicial if item["ingreso__anio"] == int(year)).next()['asignado']
        except StopIteration:
            asignado = 0
        try:
            ejecutado = (item for item in source_final if item["ingreso__anio"] == int(year)).next()['ejecutado']
        except StopIteration:
            ejecutado = 0

        # obtiene datos comparativo de todos los años
        inicial = list(IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_INICIAL, tipoingreso__clasificacion=TipoIngreso.CORRIENTE).values('ingreso__anio', 'ingreso__periodo').annotate(asignado=Sum('asignado')))
        final = list(IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_FINAL, tipoingreso__clasificacion=TipoIngreso.CORRIENTE).values('ingreso__anio', 'ingreso__periodo').annotate(ejecutado=Sum('ejecutado')))
        anual2 = glue(inicial=inicial, final=final, key='ingreso__anio')

        # obtiene datos comparativo de todos los años
        inicialg = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL, tipogasto__clasificacion=TipoGasto.CORRIENTE).values('gasto__anio', 'gasto__periodo').annotate(asignado=Sum('asignado')))
        finalg = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_FINAL, tipogasto__clasificacion=TipoGasto.CORRIENTE).values('gasto__anio', 'gasto__periodo').annotate(ejecutado=Sum('ejecutado')))
        anual2g = glue(inicial=inicialg, final=finalg, key='gasto__anio')

        # obtiene datos de gastos en ditintos rubros
        rubrosg_inicial = GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL, tipogasto__clasificacion=TipoGasto.CORRIENTE,).\
                values('tipogasto','tipogasto__nombre').order_by('tipogasto__codigo').annotate(inicial_asignado=Sum('asignado'))
        rubrosg_actualizado = GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio, gasto__periodo=PERIODO_ACTUALIZADO, tipogasto__clasificacion=TipoGasto.CORRIENTE,).\
                values('tipogasto','tipogasto__nombre').order_by('tipogasto__codigo').annotate(actualizado_asignado=Sum('asignado'), actualizado_ejecutado=Sum('ejecutado'))
        rubrosg_final = GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio, gasto__periodo=PERIODO_FINAL, tipogasto__clasificacion=TipoGasto.CORRIENTE,).\
                values('tipogasto','tipogasto__nombre').order_by('tipogasto__codigo').annotate(final_asignado=Sum('asignado'), final_ejecutado=Sum('ejecutado'))
        rubrosg_periodo = GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio, gasto__periodo=periodo, tipogasto__clasificacion=TipoGasto.CORRIENTE,).\
                values('tipogasto','tipogasto__nombre').order_by('tipogasto__codigo').annotate(asignado=Sum('asignado'), ejecutado=Sum('ejecutado'))
        rubrosg = superglue(data=(rubrosg_inicial, rubrosg_final, rubrosg_actualizado, rubrosg_periodo), key='tipogasto')

        # obtiene datos de ingresos en ditintos rubros de corriente (clasificacion 0)
        rubros_inicial = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_INICIAL, tipoingreso__clasificacion=TipoIngreso.CORRIENTE,).\
                values('tipoingreso','tipoingreso__nombre').order_by('tipoingreso__codigo').annotate(inicial_asignado=Sum('asignado'))
        rubros_actualizado = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_ACTUALIZADO, tipoingreso__clasificacion=TipoIngreso.CORRIENTE,).\
                values('tipoingreso','tipoingreso__nombre').order_by('tipoingreso__codigo').annotate(actualizado_asignado=Sum('asignado'), actualizado_ejecutado=Sum('ejecutado'))
        rubros_final = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_FINAL, tipoingreso__clasificacion=TipoIngreso.CORRIENTE,).\
                values('tipoingreso','tipoingreso__nombre').order_by('tipoingreso__codigo').annotate(final_asignado=Sum('asignado'), final_ejecutado=Sum('ejecutado'))
        rubros_periodo = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__municipio__slug=municipio, ingreso__periodo=periodo, tipoingreso__clasificacion=TipoIngreso.CORRIENTE,).\
                values('tipoingreso','tipoingreso__nombre').order_by('tipoingreso__codigo').annotate(asignado=Sum('asignado'), ejecutado=Sum('ejecutado'))
        rubros = superglue(data=(rubros_inicial, rubros_final, rubros_actualizado, rubros_periodo), key='tipoingreso')

        # obtiene clase y contador (otros en misma clase) para este año
        mi_clase = ClasificacionMunicAno.objects.get(municipio__slug=municipio, anio=year)
        mi_clase_count = ClasificacionMunicAno.objects.filter(clasificacion__clasificacion=mi_clase.clasificacion, anio=year).count()
        # obtiene clase y contador (otros en misma clase) para todos los años
        mi_clase_anios = list(ClasificacionMunicAno.objects.filter(municipio__slug=municipio).values('anio', 'clasificacion__clasificacion').annotate())
        mi_clase_anios_count = {}
        for aclase in mi_clase_anios:
            mi_clase_anios_count[aclase['anio']] = ClasificacionMunicAno.objects.filter(clasificacion__clasificacion=aclase['clasificacion__clasificacion'], anio=aclase['anio']).count()

        # grafico de ejecutado y asignado a nivel nacional (distintas clases) porcentage
        with open ("core/charts/aci_otros.sql", "r") as query_file:
            sql_tpl=query_file.read()

        sql = sql_tpl.format(quesumar="asignado", year=year, periodo=PERIODO_INICIAL, tipoingreso=TipoIngreso.CORRIENTE, mi_clase=mi_clase.clasificacion_id)
        cursor = connection.cursor()
        cursor.execute(sql)
        inicial = dictfetchall(cursor)
        sql = sql_tpl.format(quesumar="ejecutado", year=year, periodo=periodo, tipoingreso=TipoIngreso.CORRIENTE, mi_clase=mi_clase.clasificacion_id)
        cursor = connection.cursor()
        cursor.execute(sql)
        final = dictfetchall(cursor)
        sql = sql_tpl.format(quesumar="asignado", year=year, periodo=PERIODO_ACTUALIZADO, tipoingreso=TipoIngreso.CORRIENTE, mi_clase=mi_clase.clasificacion_id)
        cursor = connection.cursor()
        cursor.execute(sql)
        actualizado = dictfetchall(cursor)
        otros = glue(inicial, final, 'nombre', actualizado=actualizado)

        with open ("core/charts/aci_municipio.sql", "r") as query_file:
            sql_tpl=query_file.read()
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

        # obtiene datos comparativo de todos los años
        inicial = list(IngresoDetalle.objects.filter(ingreso__periodo=PERIODO_INICIAL, tipoingreso__clasificacion=TipoIngreso.CORRIENTE,).values('ingreso__anio', 'ingreso__periodo').order_by('ingreso__anio', 'ingreso__periodo').annotate(asignado=Sum('asignado')))
        final = list(IngresoDetalle.objects.filter(ingreso__periodo=PERIODO_FINAL, tipoingreso__clasificacion=TipoIngreso.CORRIENTE,).values('ingreso__anio', 'ingreso__periodo').order_by('ingreso__anio', 'ingreso__periodo').annotate(ejecutado=Sum('ejecutado')))
        anual2 = glue(inicial=inicial, final=final, key='ingreso__anio')

        # obtiene datos comparativo de todos los años
        inicialg = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL, tipogasto__clasificacion=TipoGasto.CORRIENTE,).values('gasto__anio', 'gasto__periodo').order_by('gasto__anio', 'gasto__periodo').annotate(asignado=Sum('asignado')))
        finalg = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL, tipogasto__clasificacion=TipoGasto.CORRIENTE,).values('gasto__anio', 'gasto__periodo').order_by('gasto__anio', 'gasto__periodo').annotate(ejecutado=Sum('ejecutado')))
        anual2g = glue(inicial=inicialg, final=finalg, key='gasto__anio')

        # obtiene datos de gastos en ditintos rubros
        rubrosg_inicial = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_INICIAL, tipogasto__clasificacion=TipoGasto.CORRIENTE,).\
                values('tipogasto','tipogasto__nombre').order_by('tipogasto__codigo').annotate(inicial_asignado=Sum('asignado'))
        rubrosg_actualizado = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_ACTUALIZADO, tipogasto__clasificacion=TipoGasto.CORRIENTE,).\
                values('tipogasto','tipogasto__nombre').order_by('tipogasto__codigo').annotate(actualizado_asignado=Sum('asignado'), actualizado_ejecutado=Sum('ejecutado'))
        rubrosg_final = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_FINAL, tipogasto__clasificacion=TipoGasto.CORRIENTE,).\
                values('tipogasto','tipogasto__nombre').order_by('tipogasto__codigo').annotate(final_asignado=Sum('asignado'), final_ejecutado=Sum('ejecutado'))
        rubrosg_periodo = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=periodo, tipogasto__clasificacion=TipoGasto.CORRIENTE,).\
                values('tipogasto','tipogasto__nombre').order_by('tipogasto__codigo').annotate(asignado=Sum('asignado'), ejecutado=Sum('ejecutado'))
        rubrosg = superglue(data=(rubrosg_inicial, rubrosg_final, rubrosg_actualizado, rubrosg_periodo), key='tipogasto')

        # obtiene datos de ingresos en ditintos rubros
        rubros_inicial = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_INICIAL, tipoingreso__clasificacion=TipoIngreso.CORRIENTE,).\
                values('tipoingreso','tipoingreso__nombre').order_by('tipoingreso__codigo').annotate(inicial_asignado=Sum('asignado'))
        rubros_actualizado = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_ACTUALIZADO, tipoingreso__clasificacion=TipoIngreso.CORRIENTE,).\
                values('tipoingreso','tipoingreso__nombre').order_by('tipoingreso__codigo').annotate(actualizado_asignado=Sum('asignado'), actualizado_ejecutado=Sum('ejecutado'))
        rubros_final = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_FINAL, tipoingreso__clasificacion=TipoIngreso.CORRIENTE,).\
                values('tipoingreso','tipoingreso__nombre').order_by('tipoingreso__codigo').annotate(final_asignado=Sum('asignado'), final_ejecutado=Sum('ejecutado'))
        rubros_periodo = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=periodo, tipoingreso__clasificacion=TipoIngreso.CORRIENTE,).\
                values('tipoingreso','tipoingreso__nombre').order_by('tipoingreso__codigo').annotate(asignado=Sum('asignado'), ejecutado=Sum('ejecutado'))
        rubros = superglue(data=(rubros_inicial, rubros_final, rubros_actualizado, rubros_periodo), key='tipoingreso')

        source_inicial = IngresoDetalle.objects.filter(ingreso__periodo=PERIODO_INICIAL, tipoingreso__clasificacion=TipoGasto.CORRIENTE).\
            values('ingreso__anio').order_by('ingreso__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_final = IngresoDetalle.objects.filter(ingreso__periodo=periodo, tipoingreso__clasificacion=TipoGasto.CORRIENTE).\
            values('ingreso__anio').order_by('ingreso__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

        # obtiene valores para este año de las listas
        try:
            asignado = (item for item in source_inicial if item["ingreso__anio"] == int(year)).next()['asignado']
        except StopIteration:
            asignado = 0
        try:
            ejecutado = (item for item in source_final if item["ingreso__anio"] == int(year)).next()['ejecutado']
        except StopIteration:
            ejecutado = 0

        # grafico de ejecutado y asignado a nivel nacional (distintas clases) porcentage
        with open ("core/charts/aci_porclasep.sql", "r") as query_file:
            sql_tpl=query_file.read()

        sql = sql_tpl.format(quesumar="asignado", year=year, periodo=PERIODO_INICIAL, tipoingreso=TipoIngreso.CORRIENTE)
        cursor = connection.cursor()
        cursor.execute(sql)
        inicial = dictfetchall(cursor)
        sql = sql_tpl.format(quesumar="ejecutado", year=year, periodo=periodo, tipoingreso=TipoIngreso.CORRIENTE)
        cursor = connection.cursor()
        cursor.execute(sql)
        final = dictfetchall(cursor)
        sql = sql_tpl.format(quesumar="asignado", year=year, periodo=PERIODO_ACTUALIZADO, tipoingreso=TipoIngreso.CORRIENTE)
        cursor = connection.cursor()
        cursor.execute(sql)
        actualizado = dictfetchall(cursor)
        porclasep = glue(inicial, final, 'clasificacion', actualizado=actualizado)

        with open ("core/charts/aci.sql", "r") as query_file:
            sql_tpl=query_file.read()
        sql = sql_tpl.format(year_list=year_list)
        cursor = connection.cursor()
        cursor.execute(sql)
        source = dictfetchall(cursor)


    data = RawDataPool(
           series=
            [{'options': {'source': source },
              'terms': [
                'anio',
                'ejecutado',
                'asignado',
                ]}
             ])

    data_ingreso = RawDataPool(
           series=
            [{'options': {'source': rubros },
              'terms': [
                'tipoingreso__nombre',
                'ejecutado',
                'asignado',
                ]}
             ])
    pie = Chart(
            datasource = data_ingreso,
            series_options =
              [{'options':{
                  'type': 'pie',},
                'terms':{
                  'tipoingreso__nombre': [
                    'ejecutado']
                  }}],
            chart_options = {
                'title': {
                  'text': u' '},
                 'yAxis': { 'title': {'text': u'Millones de córdobas'} },
                 'xAxis': { 'title': {'text': u'Años'} },
                },
            )

    bar = Chart(
            datasource = data_ingreso,
            series_options =
              [{'options':{
                  'type': 'column',},
                'terms':{
                  'tipoingreso__nombre': [
                    'ejecutado']
                  }}],
            chart_options = {
                'title': {
                  'text': u' '},
                 'yAxis': { 'title': {'text': u'Millones de córdobas'} },
                 'xAxis': { 'title': {'text': u'Rubros'} },
                },
            #x_sortf_mapf_mts = (None, lambda i:  i.strftime('%Y'), False)
            )

    # FIXME BS
    porclase = None

    reporte = request.POST.get("reporte","")
    if "excel" in request.POST.keys() and reporte:
        from core.utils import obtener_excel_response
        data = {'charts': (bar, ), \
            'mi_clase': mi_clase, 'municipio': municipio_row, 'year': year, 'source': source, \
            'ejecutado': ejecutado, 'asignado': asignado, 'year_list': year_list, 'municipio_list': municipio_list, \
            'anuales': anual2, 'anualesg': anual2g, 'porclase': porclase, 'porclasep': porclasep, 'rubros': rubros, 'rubrosg': rubrosg, 'otros': otros}
        return obtener_excel_response(reporte=reporte, data=data)


    return render_to_response('variance_analysis.html',{'charts': (bar, pie), 'source': source, \
            'indicator_name': "Ahorro Corriente", \
            'indicator_description': "El indicador de Ahorro corriente o capacidad de ahorro es el balance entre los ingresos corrientes y los gastos corrientes y es igual al ahorro corriente como porcentaje de los ingresos corriente​s. Este indicador es una medida de la solvencia que tiene la municipalidad para generar excedentes propios que se destinen a inversión, complementariamente al uso de transferencias del Gobierno Central y la regalías. Se espera que este indicador sea positivo, es decir, que las municipalidades generen ahorro.", \
            'mi_clase': mi_clase, 'municipio': municipio_row, 'year': year, \
            'ejecutado': ejecutado, 'asignado': asignado, 'year_list': year_list, 'municipio_list': municipio_list, \
            'anuales': anual2, 'anualesg': anual2g, 'porclase': porclase, 'porclasep': porclasep, 'rubros': rubros, 'rubrosg': rubrosg, 'otros': otros},\
            context_instance=RequestContext(request))
