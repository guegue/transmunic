# -*- coding: utf-8 -*-

from itertools import chain
from datetime import datetime, time

from django.db import connection
from django.db.models import Q, Sum, Max, Min, Avg, Count
from django.shortcuts import render_to_response
from django.template import RequestContext

from chartit import DataPool, Chart, PivotDataPool, PivotChart, RawDataPool

from core.models import IngresoDetalle, Ingreso, GastoDetalle, Gasto, Inversion, Proyecto, Municipio, TipoGasto, TipoIngreso, InversionFuente, InversionFuenteDetalle, CatInversion, ClasificacionMunicAno
from core.models import Anio, getYears, dictfetchall, glue
from core.models import PERIODO_INICIAL, PERIODO_ACTUALIZADO, PERIODO_FINAL, PERIODO_VERBOSE
from core.charts.misc import getVar

def ep_chart(request):

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

        # grafico de ejecutado y asignado a nivel nacional (distintas clases) porcentage
        with open ("core/charts/ep_porclasep.sql", "r") as query_file:
            sql_tpl=query_file.read()
        
        sql = sql_tpl.format(quesumar="asignado", year=year, periodo=PERIODO_INICIAL, tipoingreso=TipoIngreso.CORRIENTE, notipoingreso=TipoIngreso.TRANSFERENCIAS_CORRIENTES, )
        cursor = connection.cursor()
        cursor.execute(sql)
        inicial = dictfetchall(cursor)
        sql = sql_tpl.format(quesumar="ejecutado", year=year, periodo=PERIODO_FINAL, tipoingreso=TipoIngreso.CORRIENTE, notipoingreso=TipoIngreso.TRANSFERENCIAS_CORRIENTES, )
        cursor = connection.cursor()
        cursor.execute(sql)
        final = dictfetchall(cursor)
        sql = sql_tpl.format(quesumar="ejecutado", year=year, periodo=PERIODO_ACTUALIZADO, tipoingreso=TipoIngreso.CORRIENTE, notipoingreso=TipoIngreso.TRANSFERENCIAS_CORRIENTES, )
        cursor = connection.cursor()
        cursor.execute(sql)
        actualizado = dictfetchall(cursor)
        porclasep = glue(inicial, final, PERIODO_INICIAL, 'clasificacion', actualizado=actualizado)

        with open ("core/charts/ep.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [year_list])
    data = RawDataPool(
           series=
            [{'options': {'source': source },
              'terms': [
                'anio',
                'ejecutado',
                ]}
             ])

    bar = Chart(
            datasource = data,
            series_options =
              [{'options':{
                  'type': 'bar',},
                'terms':{
                  'anio': [
                    'ejecutado']
                  }}],
            chart_options = {
                'title': {
                  'text': u'Ejecución del presupuesto %s ' % (municipio,)},
                },
            #x_sortf_mapf_mts = (None, lambda i:  i.strftime('%Y'), False)
            )

    # FIXME BS
    ejecutado = asignado = anual2 = anual2g = porclase = rubros = rubrosg = None

    return render_to_response('ep.html',{'charts': (bar, ), \
            'mi_clase': mi_clase, 'municipio': municipio_row, 'year': year, \
            'ejecutado': ejecutado, 'asignado': asignado, 'year_list': year_list, 'municipio_list': municipio_list, \
            'anuales': anual2, 'anualesg': anual2g, 'porclase': porclase, 'porclasep': porclasep, 'rubros': rubros, 'rubrosg': rubrosg, 'otros': otros},\
            context_instance=RequestContext(request))
