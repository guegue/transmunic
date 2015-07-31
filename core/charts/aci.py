# -*- coding: utf-8 -*-

from itertools import chain
from datetime import datetime, time

from django.db import connection
from django.db.models import Q, Sum, Max, Min, Avg, Count
from django.shortcuts import render_to_response
from django.template import RequestContext

from chartit import DataPool, Chart, PivotDataPool, PivotChart, RawDataPool

from core.models import IngresoDetalle, Ingreso, GastoDetalle, Gasto, Inversion, Proyecto, Municipio, TipoIngreso, TipoGasto, InversionFuente, InversionFuenteDetalle, CatInversion, ClasificacionMunicAno
from core.models import Anio, getYears, dictfetchall, glue
from core.models import PERIODO_INICIAL, PERIODO_ACTUALIZADO, PERIODO_FINAL, PERIODO_VERBOSE
from core.charts.misc import getVar


def aci_chart(request, municipio=None, year=None, portada=False):

    municipio_list = Municipio.objects.all()
    municipio = getVar('municipio', request)
    year_list = getYears(Gasto)
    year = getVar('year', request)
    if not year:
        year = year_list[-1]

    periodo = Anio.objects.get(anio=year).periodo
    quesumar = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'

    if municipio:
        municipio_row = Municipio.objects.get(slug=municipio)
        municipio_id = municipio_row.id
        municipio_nombre = municipio_row.nombre
        rubrosg = None
        porclasep = None

        source_inicial = IngresoDetalle.objects.filter(ingreso__periodo=PERIODO_INICIAL, \
            ingreso__municipio__slug=municipio, tipoingreso__clasificacion=TipoGasto.CORRIENTE).\
            values('ingreso__anio').order_by('ingreso__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_final = IngresoDetalle.objects.filter(ingreso__periodo=PERIODO_FINAL, \
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
        inicial = list(IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_INICIAL, tipoingreso__clasificacion=TipoGasto.CORRIENTE).values('ingreso__anio', 'ingreso__periodo').annotate(asignado=Sum('asignado')))
        final = list(IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_FINAL, tipoingreso__clasificacion=TipoGasto.CORRIENTE).values('ingreso__anio', 'ingreso__periodo').annotate(ejecutado=Sum('ejecutado')))
        anual2 = glue(inicial=inicial, final=final, periodo=PERIODO_INICIAL, key='ingreso__anio')

        # obtiene datos comparativo de todos los años
        inicialg = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL, tipogasto__clasificacion=TipoGasto.CORRIENTE).values('gasto__anio', 'gasto__periodo').annotate(asignado=Sum('asignado')))
        finalg = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_FINAL, tipogasto__clasificacion=TipoGasto.CORRIENTE).values('gasto__anio', 'gasto__periodo').annotate(ejecutado=Sum('ejecutado')))
        anual2g = glue(inicial=inicialg, final=finalg, periodo=PERIODO_INICIAL, key='gasto__anio')

        # obtiene datos de gastos en ditintos rubros
        rubrosg_inicial = GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL, tipogasto__clasificacion=TipoGasto.CORRIENTE,).\
                values('tipogasto','tipogasto__nombre').order_by('tipogasto__codigo').annotate(asignado=Sum('asignado'))
        rubrosg_actualizado = GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio, gasto__periodo=PERIODO_ACTUALIZADO, tipogasto__clasificacion=TipoGasto.CORRIENTE,).\
                values('tipogasto','tipogasto__nombre').order_by('tipogasto__codigo').annotate(ejecutado=Sum('ejecutado'))
        rubrosg_final= GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio, gasto__periodo=PERIODO_FINAL, tipogasto__clasificacion=TipoGasto.CORRIENTE,).\
                values('tipogasto','tipogasto__nombre').order_by('tipogasto__codigo').annotate(ejecutado=Sum('ejecutado'))
        rubrosg = glue(rubrosg_inicial, rubrosg_final, periodo, 'tipogasto', actualizado=rubrosg_actualizado)

        # obtiene datos de ingresos en ditintos rubros de corriente (clasificacion 0)
        rubros_inicial = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_INICIAL, tipoingreso__clasificacion=TipoIngreso.CORRIENTE,).\
                values('tipoingreso','tipoingreso__nombre').order_by('tipoingreso__codigo').annotate(asignado=Sum('asignado'))
        rubros_actualizado = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_ACTUALIZADO, tipoingreso__clasificacion=TipoIngreso.CORRIENTE,).\
                values('tipoingreso','tipoingreso__nombre').order_by('tipoingreso__codigo').annotate(ejecutado=Sum('ejecutado'))
        rubros_final= IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_FINAL, tipoingreso__clasificacion=TipoIngreso.CORRIENTE,).\
                values('tipoingreso','tipoingreso__nombre').order_by('tipoingreso__codigo').annotate(ejecutado=Sum('ejecutado'))
        rubros = glue(rubros_inicial, rubros_final, periodo, 'tipoingreso', actualizado=rubros_actualizado)

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
        sql = sql_tpl.format(quesumar="ejecutado", year=year, periodo=PERIODO_FINAL, tipoingreso=TipoIngreso.CORRIENTE, mi_clase=mi_clase.clasificacion_id)
        cursor = connection.cursor()
        cursor.execute(sql)
        final = dictfetchall(cursor)
        sql = sql_tpl.format(quesumar="ejecutado", year=year, periodo=PERIODO_ACTUALIZADO, tipoingreso=TipoIngreso.CORRIENTE, mi_clase=mi_clase.clasificacion_id)
        cursor = connection.cursor()
        cursor.execute(sql)
        actualizado = dictfetchall(cursor)
        otros = glue(inicial, final, PERIODO_INICIAL, 'nombre', actualizado=actualizado)

        with open ("core/charts/aci_municipio.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [municipio, municipio, municipio, municipio, municipio, municipio, year_list])
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
        anual2 = glue(inicial=inicial, final=final, periodo=PERIODO_INICIAL, key='ingreso__anio')

        # obtiene datos comparativo de todos los años
        inicialg = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL, tipogasto__clasificacion=TipoGasto.CORRIENTE,).values('gasto__anio', 'gasto__periodo').order_by('gasto__anio', 'gasto__periodo').annotate(asignado=Sum('asignado')))
        finalg = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL, tipogasto__clasificacion=TipoGasto.CORRIENTE,).values('gasto__anio', 'gasto__periodo').order_by('gasto__anio', 'gasto__periodo').annotate(ejecutado=Sum('ejecutado')))
        anual2g = glue(inicial=inicialg, final=finalg, periodo=PERIODO_INICIAL, key='gasto__anio')

        # obtiene datos de gastos en ditintos rubros
        rubrosg_inicial = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_INICIAL, tipogasto__clasificacion=TipoGasto.CORRIENTE,).\
                values('tipogasto','tipogasto__nombre').order_by('tipogasto__codigo').annotate(asignado=Sum('asignado'))
        rubrosg_actualizado = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_ACTUALIZADO, tipogasto__clasificacion=TipoGasto.CORRIENTE,).\
                values('tipogasto','tipogasto__nombre').order_by('tipogasto__codigo').annotate(ejecutado=Sum('ejecutado'))
        rubrosg_final= GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_FINAL, tipogasto__clasificacion=TipoGasto.CORRIENTE,).\
                values('tipogasto','tipogasto__nombre').order_by('tipogasto__codigo').annotate(ejecutado=Sum('ejecutado'))
        rubrosg = glue(rubrosg_inicial, rubrosg_final, periodo, 'tipogasto', actualizado=rubrosg_actualizado)

        # obtiene datos de ingresos en ditintos rubros
        rubros_inicial = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_INICIAL, tipoingreso__clasificacion=TipoIngreso.CORRIENTE,).\
                values('tipoingreso','tipoingreso__nombre').order_by('tipoingreso__codigo').annotate(asignado=Sum('asignado'))
        rubros_actualizado = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_ACTUALIZADO, tipoingreso__clasificacion=TipoIngreso.CORRIENTE,).\
                values('tipoingreso','tipoingreso__nombre').order_by('tipoingreso__codigo').annotate(ejecutado=Sum('ejecutado'))
        rubros_final= IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_FINAL, tipoingreso__clasificacion=TipoIngreso.CORRIENTE,).\
                values('tipoingreso','tipoingreso__nombre').order_by('tipoingreso__codigo').annotate(ejecutado=Sum('ejecutado'))
        rubros = glue(rubros_inicial, rubros_final, periodo, 'tipoingreso', actualizado=rubros_actualizado)

        source_inicial = IngresoDetalle.objects.filter(ingreso__periodo=PERIODO_INICIAL, tipoingreso__clasificacion=TipoGasto.CORRIENTE).\
            values('ingreso__anio').order_by('ingreso__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_final = IngresoDetalle.objects.filter(ingreso__periodo=PERIODO_FINAL, tipoingreso__clasificacion=TipoGasto.CORRIENTE).\
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
        sql = sql_tpl.format(quesumar="ejecutado", year=year, periodo=PERIODO_FINAL, tipoingreso=TipoIngreso.CORRIENTE)
        cursor = connection.cursor()
        cursor.execute(sql)
        final = dictfetchall(cursor)
        sql = sql_tpl.format(quesumar="ejecutado", year=year, periodo=PERIODO_ACTUALIZADO, tipoingreso=TipoIngreso.CORRIENTE)
        cursor = connection.cursor()
        cursor.execute(sql)
        actualizado = dictfetchall(cursor)
        porclasep = glue(inicial, final, PERIODO_INICIAL, 'clasificacion', actualizado=actualizado)

        with open ("core/charts/aci.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [year_list])
    data = RawDataPool(
           series=
            [{'options': {'source': source },
              'terms': [
                'anio',
                'ejecutado',
                'asignado',
                ]}
             ])
    bar = Chart(
            datasource = data,
            series_options =
              [{'options':{
                  'type': 'bar',},
                'terms':{
                  'anio': [
                    'asignado',
                    'ejecutado']
                  }}],
            chart_options = {
                'title': {
                  'text': u'Ahorro corriente para inversiones %s ' % (municipio,)},
                },
            #x_sortf_mapf_mts = (None, lambda i:  i.strftime('%Y'), False)
            )


    # FIXME BS
    porclase = None

    return render_to_response('aci.html',{'charts': (bar, ), \
            'mi_clase': mi_clase, 'municipio': municipio_row, 'anio': year, \
            'ejecutado': ejecutado, 'asignado': asignado, 'year_list': year_list, 'municipio_list': municipio_list, \
            'anuales': anual2, 'anualesg': anual2g, 'porclase': porclase, 'porclasep': porclasep, 'rubros': rubros, 'rubrosg': rubrosg, 'otros': otros},\
            context_instance=RequestContext(request))
