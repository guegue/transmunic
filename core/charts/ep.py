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
from core.models import PERIODO_INICIAL, PERIODO_ACTUALIZADO, PERIODO_FINAL, PERIODO_VERBOSE, CLASIFICACION_VERBOSE
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
        porclasep = None

        # obtiene datos de gastos en ditintos rubros
        rubrosg_inicial = GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL,).\
                values('tipogasto__clasificacion',).order_by('tipogasto__clasificacion').annotate(asignado=Sum('asignado'))
        rubrosg_actualizado = GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio, gasto__periodo=PERIODO_ACTUALIZADO,).\
                values('tipogasto__clasificacion',).order_by('tipogasto__clasificacion').annotate(ejecutado=Sum('ejecutado'))
        rubrosg_final= GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio, gasto__periodo=PERIODO_FINAL,).\
                values('tipogasto__clasificacion').order_by('tipogasto__clasificacion').annotate(ejecutado=Sum('ejecutado'))
        rubrosg = glue(rubrosg_inicial, rubrosg_final, periodo, 'tipogasto__clasificacion', actualizado=rubrosg_actualizado)
        for r in rubrosg:
            r['tipogasto__clasificacion'] = CLASIFICACION_VERBOSE[r['tipogasto__clasificacion']]

        # obtiene datos de ingresos en ditintos rubros de corriente (clasificacion 0)
        rubros_inicial = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_INICIAL,).\
                values('tipoingreso__clasificacion').order_by('tipoingreso__clasificacion').annotate(asignado=Sum('asignado'))
        rubros_actualizado = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_ACTUALIZADO,).\
                values('tipoingreso__clasificacion').order_by('tipoingreso__clasificacion').annotate(ejecutado=Sum('ejecutado'))
        rubros_final= IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_FINAL,).\
                values('tipoingreso__clasificacion').order_by('tipoingreso__clasificacion').annotate(ejecutado=Sum('ejecutado'))
        rubros = glue(rubros_inicial, rubros_final, periodo, 'tipoingreso__clasificacion', actualizado=rubros_actualizado)
        for r in rubros:
            r['tipoingreso__clasificacion'] = CLASIFICACION_VERBOSE[r['tipoingreso__clasificacion']]

        # obtiene clase y contador (otros en misma clase) para este año
        mi_clase = ClasificacionMunicAno.objects.get(municipio__slug=municipio, anio=year)
        mi_clase_count = ClasificacionMunicAno.objects.filter(clasificacion__clasificacion=mi_clase.clasificacion, anio=year).count()
        # obtiene clase y contador (otros en misma clase) para todos los años
        mi_clase_anios = list(ClasificacionMunicAno.objects.filter(municipio__slug=municipio).values('anio', 'clasificacion__clasificacion').annotate())
        mi_clase_anios_count = {}

        for aclase in mi_clase_anios:
            mi_clase_anios_count[aclase['anio']] = ClasificacionMunicAno.objects.filter(clasificacion__clasificacion=aclase['clasificacion__clasificacion'], anio=aclase['anio']).count()

        # obtiene datos comparativo de todos los años
        inicial = list(IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_INICIAL,).values('ingreso__anio', 'ingreso__periodo').annotate(asignado=Sum('asignado')))
        final = list(IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_FINAL,).values('ingreso__anio', 'ingreso__periodo').annotate(ejecutado=Sum('ejecutado')))
        anual2 = glue(inicial=inicial, final=final, periodo=PERIODO_INICIAL, key='ingreso__anio')

        # obtiene datos comparativo de todos los años
        inicialg = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL,).values('gasto__anio', 'gasto__periodo').annotate(asignado=Sum('asignado')))
        finalg = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_FINAL,).values('gasto__anio', 'gasto__periodo').annotate(ejecutado=Sum('ejecutado')))
        anual2g = glue(inicial=inicialg, final=finalg, periodo=PERIODO_INICIAL, key='gasto__anio')

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
                values('tipogasto__clasificacion',).order_by('tipogasto__clasificacion').annotate(asignado=Sum('asignado'))
        rubrosg_actualizado = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_ACTUALIZADO,).\
                values('tipogasto__clasificacion',).order_by('tipogasto__clasificacion').annotate(ejecutado=Sum('ejecutado'))
        rubrosg_final= GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_FINAL,).\
                values('tipogasto__clasificacion').order_by('tipogasto__clasificacion').annotate(ejecutado=Sum('ejecutado'))
        rubrosg = glue(rubrosg_inicial, rubrosg_final, periodo, 'tipogasto__clasificacion', actualizado=rubrosg_actualizado)
        for r in rubrosg:
            r['tipogasto__clasificacion'] = CLASIFICACION_VERBOSE[r['tipogasto__clasificacion']]

        # obtiene datos de ingresos en ditintos rubros de corriente (clasificacion 0)
        rubros_inicial = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_INICIAL,).\
                values('tipoingreso__clasificacion').order_by('tipoingreso__clasificacion').annotate(asignado=Sum('asignado'))
        rubros_actualizado = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_ACTUALIZADO,).\
                values('tipoingreso__clasificacion').order_by('tipoingreso__clasificacion').annotate(ejecutado=Sum('ejecutado'))
        rubros_final= IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_FINAL,).\
                values('tipoingreso__clasificacion').order_by('tipoingreso__clasificacion').annotate(ejecutado=Sum('ejecutado'))
        rubros = glue(rubros_inicial, rubros_final, periodo, 'tipoingreso__clasificacion', actualizado=rubros_actualizado)
        for r in rubros:
            r['tipoingreso__clasificacion'] = CLASIFICACION_VERBOSE[r['tipoingreso__clasificacion']]

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

        # obtiene datos comparativo de todos los años
        inicial = list(IngresoDetalle.objects.filter(ingreso__periodo=PERIODO_INICIAL,).values('ingreso__anio', 'ingreso__periodo').annotate(asignado=Sum('asignado')))
        final = list(IngresoDetalle.objects.filter(ingreso__periodo=PERIODO_FINAL,).values('ingreso__anio', 'ingreso__periodo').annotate(ejecutado=Sum('ejecutado')))
        anual2 = glue(inicial=inicial, final=final, periodo=PERIODO_INICIAL, key='ingreso__anio')

        # obtiene datos comparativo de todos los años
        inicialg = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL,).values('gasto__anio', 'gasto__periodo').annotate(asignado=Sum('asignado')))
        finalg = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL,).values('gasto__anio', 'gasto__periodo').annotate(ejecutado=Sum('ejecutado')))
        anual2g = glue(inicial=inicialg, final=finalg, periodo=PERIODO_INICIAL, key='gasto__anio')

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
    otros = ejecutado = asignado = porclase = None

    return render_to_response('ep.html',{'charts': (bar, ), \
            'mi_clase': mi_clase, 'municipio': municipio_row, 'year': year, \
            'ejecutado': ejecutado, 'asignado': asignado, 'year_list': year_list, 'municipio_list': municipio_list, \
            'anuales': anual2, 'anualesg': anual2g, 'porclase': porclase, 'porclasep': porclasep, 'rubros': rubros, 'rubrosg': rubrosg, 'otros': otros},\
            context_instance=RequestContext(request))
