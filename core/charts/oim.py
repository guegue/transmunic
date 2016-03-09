# -*- coding: utf-8 -*-
##############################################################################
#
# OIM charts /core/oim
#
##############################################################################

from itertools import chain
from datetime import datetime, time
from operator import itemgetter

from django.db import connection
from django.db.models import Q, Sum, Max, Min, Avg, Count
from django.shortcuts import render_to_response
from django.template import RequestContext

from chartit import DataPool, Chart, PivotDataPool, PivotChart, RawDataPool

from core.models import Anio, IngresoDetalle, Ingreso, TipoIngreso, OrigenRecurso, GastoDetalle, Gasto, Inversion, Proyecto, Municipio, TipoGasto, InversionFuente, InversionFuenteDetalle, CatInversion, ClasificacionMunicAno
from core.models import PERIODO_INICIAL, PERIODO_ACTUALIZADO, PERIODO_FINAL, PERIODO_VERBOSE
from core.tools import getYears, dictfetchall, glue, superglue
from lugar.models import Poblacion

def oim_chart(municipio=None, year=None, portada=False):
    municipio_list = Municipio.objects.all()
    year_list = getYears(Ingreso)
    if not year:
        year = year_list[-2]

    # obtiene último periodo del año que se quiere ver
    year_data = Anio.objects.get(anio=year)
    periodo = year_data.periodo

    # usar 'asignado' para todo periodo si estamos en portada
    if portada:
        quesumar = 'asignado'
    else:
        quesumar = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'

    ChartError = False

    if municipio:
        porclase = None
        porclasep = None
        municipio_row = Municipio.objects.get(slug=municipio)
        municipio_id = municipio_row.id
        municipio_nombre = municipio_row.nombre

        source = IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio, ingreso__anio=year).values('subsubtipoingreso__origen__id', 'subsubtipoingreso__origen__nombre').annotate(**{quesumar: Sum(quesumar)}).order_by('subsubtipoingreso__origen__nombre')
        tipos_inicial = IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio, ingreso__anio=year, ingreso__periodo=PERIODO_INICIAL).values('subsubtipoingreso__origen__nombre', 'subsubtipoingreso__origen__id').annotate(asignado=Sum('asignado')).order_by('subsubtipoingreso__origen__id')
        tipos_final = IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio, ingreso__anio=year, ingreso__periodo=periodo).values('subsubtipoingreso__origen__nombre', 'subsubtipoingreso__origen__id').annotate(ejecutado=Sum('ejecutado')).order_by('subsubtipoingreso__origen__id')
        sources = glue(tipos_inicial, tipos_final, 'subsubtipoingreso__origen__id')
        source_barra = IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio, ingreso__periodo=periodo)
        source_barra2 = IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio, ingreso__periodo=periodo, ingreso__anio__gt=year_list[-3])

        source_inicial = IngresoDetalle.objects.filter(ingreso__periodo=PERIODO_INICIAL, \
            ingreso__municipio__slug=municipio).\
            values('ingreso__anio').order_by('ingreso__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_final = IngresoDetalle.objects.filter(ingreso__periodo=PERIODO_FINAL, \
            ingreso__municipio__slug=municipio).\
            values('ingreso__anio').order_by('ingreso__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_periodo = IngresoDetalle.objects.filter(ingreso__periodo=periodo, \
            ingreso__municipio__slug=municipio).\
            values('ingreso__anio').order_by('ingreso__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

        # obtiene valores para este año de las listas
        try:
            asignado = (item for item in source_inicial if item["ingreso__anio"] == int(year)).next()['asignado']
        except StopIteration:
            asignado = 0
        try:
            ejecutado = (item for item in source_periodo if item["ingreso__anio"] == int(year)).next()['ejecutado']
        except StopIteration:
            ejecutado = 0

        # obtiene datos de ingresos en ditintos rubros de persoal pemanente (codigo 1100000)
        rubrosp_inicial = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_INICIAL, \
                subsubtipoingreso__origen=OrigenRecurso.RECAUDACION,).\
                values('subtipoingreso__codigo','subtipoingreso__nombre').order_by('subtipoingreso__codigo').annotate(inicial_asignado=Sum('asignado'))
        rubrosp_actualizado = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_ACTUALIZADO, \
                subsubtipoingreso__origen=OrigenRecurso.RECAUDACION,).\
                values('subtipoingreso__codigo','subtipoingreso__nombre').order_by('subtipoingreso__codigo').annotate(actualizado_asignado=Sum('asignado'), actualizado_ejectuado=Sum('ejecutado'))
        rubrosp_final = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_FINAL, \
                subsubtipoingreso__origen=OrigenRecurso.RECAUDACION,).\
                values('subtipoingreso__codigo','subtipoingreso__nombre').order_by('subtipoingreso__codigo').annotate(final_asignado=Sum('asignado'), final_ejecutado=Sum('ejecutado'))
        rubrosp_periodo = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__municipio__slug=municipio, ingreso__periodo=periodo, \
                subsubtipoingreso__origen=OrigenRecurso.RECAUDACION,).\
                values('subtipoingreso__codigo','subtipoingreso__nombre').order_by('subtipoingreso__codigo').annotate(ejecutado=Sum('ejecutado'))
        rubrosp = superglue(data=(rubrosp_inicial, rubrosp_final, rubrosp_actualizado, rubrosp_periodo), key='subtipoingreso__codigo')

        # obtiene datos de ingresos en ditintos rubros de corriente (clasificacion 0)
        rubros_inicial = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_INICIAL,).\
                values('subsubtipoingreso__origen__id','subsubtipoingreso__origen__nombre').order_by('subsubtipoingreso__origen__id').annotate(inicial_asignado=Sum('asignado'))
        rubros_actualizado = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_ACTUALIZADO,).\
                values('subsubtipoingreso__origen__id','subsubtipoingreso__origen__nombre').order_by('subsubtipoingreso__origen__id').annotate(actualizado_ejecutado=Sum('ejecutado'), actualizado_asignado=Sum('asignado'))
        rubros_final = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_FINAL,).\
                values('subsubtipoingreso__origen__id','subsubtipoingreso__origen__nombre').order_by('subsubtipoingreso__origen__id').annotate(final_ejecutado=Sum('ejecutado'), final_asignado=Sum('asignado'))
        rubros_periodo = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__municipio__slug=municipio, ingreso__periodo=periodo,).\
                values('subsubtipoingreso__origen__id','subsubtipoingreso__origen__nombre').order_by('subsubtipoingreso__origen__id').annotate(ejecutado=Sum('ejecutado'))
        rubros = superglue(data=(rubros_inicial, rubros_final, rubros_actualizado, rubros_periodo), key='subsubtipoingreso__origen__id')

        # obtiene clase y contador (otros en misma clase) para este año
        mi_clase = ClasificacionMunicAno.objects.get(municipio__slug=municipio, anio=year)
        mi_clase_count = ClasificacionMunicAno.objects.filter(clasificacion__clasificacion=mi_clase.clasificacion, anio=year).count()
        # obtiene clase y contador (otros en misma clase) para todos los años
        mi_clase_anios = list(ClasificacionMunicAno.objects.filter(municipio__slug=municipio).values('anio', 'clasificacion__clasificacion').annotate())
        mi_clase_anios_count = {}
        for aclase in mi_clase_anios:
            mi_clase_anios_count[aclase['anio']] = ClasificacionMunicAno.objects.filter(clasificacion__clasificacion=aclase['clasificacion__clasificacion'], anio=aclase['anio']).count()

        # obtiene datos de municipios de la misma clase
        municipios_inicial = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_INICIAL, ingreso__municipio__clase__anio=year, \
                ingreso__municipio__clasificaciones__clasificacion=mi_clase.clasificacion).\
                values('ingreso__municipio__nombre', 'ingreso__municipio__slug').order_by('ingreso__municipio__nombre').annotate(asignado=Sum('asignado'))
        municipios_actualizado = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_ACTUALIZADO, ingreso__municipio__clase__anio=year, \
                ingreso__municipio__clasificaciones__clasificacion=mi_clase.clasificacion).\
                values('ingreso__municipio__nombre', 'ingreso__municipio__slug').order_by('ingreso__municipio__nombre').annotate(asignado=Sum('asignado'))
        municipios_final = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=periodo, ingreso__municipio__clase__anio=year, \
                ingreso__municipio__clasificaciones__clasificacion=mi_clase.clasificacion).\
                values('ingreso__municipio__nombre', 'ingreso__municipio__slug').order_by('ingreso__municipio__nombre').annotate(ejecutado=Sum('ejecutado'))
        otros = glue(municipios_inicial, municipios_final, 'ingreso__municipio__nombre', actualizado=municipios_actualizado)
        # inserta porcentages de total de ingresos
        for row in otros:
            #total_poblacion = Poblacion.objects.filter(anio=year, municipio__clasificaciones__clasificacion=mi_clase.clasificacion)\
            #        .aggregate(poblacion=Sum('poblacion'))['poblacion']
            try:
                total_poblacion = Poblacion.objects.get(anio=year, municipio__slug=row['ingreso__municipio__slug']).poblacion
            except:
                total_poblacion = 0
            row['poblacion'] = total_poblacion
            row['ejecutado_percent'] = round(row['ejecutado'] / total_poblacion * 100, 1) if total_poblacion > 0 else 0
            row['asignado_percent'] = round(row['asignado'] / total_poblacion * 100, 1) if total_poblacion > 0 else 0
        otros = sorted(otros, key=itemgetter('ejecutado_percent'), reverse=True)

        # obtiene datos para grafico comparativo de tipo de ingresos
        tipo_inicial= list(IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio, ingreso__anio=year, ingreso__periodo=PERIODO_INICIAL).values('subsubtipoingreso__origen__nombre').annotate(asignado=Sum('asignado')))
        tipo_final = list(IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio, ingreso__anio=year, ingreso__periodo=PERIODO_FINAL).values('subsubtipoingreso__origen__nombre').annotate(ejecutado=Sum('ejecutado')))
        tipo = glue(tipo_inicial, tipo_final, 'subsubtipoingreso__origen__nombre')

        # obtiene datos comparativo de todos los años FIXME: replaces data below?
        inicial = list(IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_INICIAL).values('ingreso__anio', 'ingreso__periodo').annotate(asignado=Sum('asignado')))
        final = list(IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_FINAL).values('ingreso__anio', 'ingreso__periodo').annotate(ejecutado=Sum('ejecutado')))
        anual2 = glue(inicial=inicial, final=final, key='ingreso__anio')
        final_clase_sql = "SELECT core_ingreso.anio AS ingreso__anio,'F' AS ingreso__periodo,SUM(ejecutado) AS clase_final FROM core_ingresodetalle JOIN core_ingreso ON core_ingresodetalle.ingreso_id=core_ingreso.id \
        JOIN lugar_clasificacionmunicano ON core_ingreso.municipio_id=lugar_clasificacionmunicano.municipio_id AND \
        core_ingreso.anio=lugar_clasificacionmunicano.anio JOIN core_tipoingreso ON core_ingresodetalle.tipoingreso_id=core_tipoingreso.codigo \
        WHERE core_ingreso.periodo=%s \
        AND lugar_clasificacionmunicano.clasificacion_id=(SELECT clasificacion_id FROM lugar_clasificacionmunicano WHERE municipio_id=%s AND lugar_clasificacionmunicano.anio=core_ingreso.anio) \
        GROUP BY core_ingreso.anio"
        cursor = connection.cursor()
        cursor.execute(final_clase_sql, [PERIODO_FINAL, municipio_id])
        final_clase = dictfetchall(cursor)
        for row in anual2:
            found = False
            for row2 in final_clase:
                if row2['ingreso__anio'] == row['ingreso__anio']:
                    found = True
                    try:
                        row['clase_final'] = row2['clase_final'] / mi_clase_anios_count[row['ingreso__anio']]
                    except KeyError:
                        row['clase_final'] = 0
            if not found:
                row['clase_final'] = 0
        comparativo_anios = anual2

        # obtiene datos para OIM comparativo de todos los años
        inicial = list(IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_INICIAL).values('ingreso__anio', 'ingreso__periodo').annotate(municipio_inicial=Sum('asignado')))
        final = list(IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio, ingreso__periodo=PERIODO_FINAL).values('ingreso__anio', 'ingreso__periodo').annotate(municipio_final=Sum('ejecutado')))

        # obtiene datos para municipio de la misma clase
        inicial_clase_sql = "SELECT core_ingreso.anio AS ingreso__anio,SUM(asignado) AS clase_inicial FROM core_ingresodetalle JOIN core_ingreso ON core_ingresodetalle.ingreso_id=core_ingreso.id \
        JOIN lugar_clasificacionmunicano ON core_ingreso.municipio_id=lugar_clasificacionmunicano.municipio_id AND \
        core_ingreso.anio=lugar_clasificacionmunicano.anio WHERE core_ingreso.periodo=%s \
        AND lugar_clasificacionmunicano.clasificacion_id=(SELECT clasificacion_id FROM lugar_clasificacionmunicano WHERE municipio_id=%s AND lugar_clasificacionmunicano.anio=core_ingreso.anio) \
        GROUP BY core_ingreso.anio"
        cursor = connection.cursor()
        cursor.execute(inicial_clase_sql, [PERIODO_INICIAL, municipio_id])
        inicial_clase = dictfetchall(cursor)
        final_clase_sql = "SELECT core_ingreso.anio AS ingreso__anio,SUM(ejecutado) AS clase_final FROM core_ingresodetalle JOIN core_ingreso ON core_ingresodetalle.ingreso_id=core_ingreso.id \
        JOIN lugar_clasificacionmunicano ON core_ingreso.municipio_id=lugar_clasificacionmunicano.municipio_id AND \
        core_ingreso.anio=lugar_clasificacionmunicano.anio WHERE core_ingreso.periodo=%s \
        AND lugar_clasificacionmunicano.clasificacion_id=(SELECT clasificacion_id FROM lugar_clasificacionmunicano WHERE municipio_id=%s AND lugar_clasificacionmunicano.anio=core_ingreso.anio) \
        GROUP BY core_ingreso.anio"
        cursor = connection.cursor()
        cursor.execute(final_clase_sql, [PERIODO_FINAL, municipio_id])
        final_clase = dictfetchall(cursor)

        # inserta datos para municipio de la misma clase
        for row in inicial:
            for row2 in inicial_clase:
                if row2['ingreso__anio'] == row['ingreso__anio']:
                    row['clase_inicial'] = row2['clase_inicial'] / mi_clase_anios_count[row['ingreso__anio']]
        for row in final:
            for row2 in final_clase:
                if row2['ingreso__anio'] == row['ingreso__anio']:
                    row['clase_final'] = row2['clase_final'] / mi_clase_anios_count[row['ingreso__anio']]
        for row in inicial:
            found = False
            for row2 in final:
                if row2['ingreso__anio'] == row['ingreso__anio']:
                    found = True
                    row['clase_final'] = row2['clase_final']
                    row['municipio_final'] = row2['municipio_final']
                if not found:
                    row['clase_final'] = 0
                    row['municipio_final'] = 0
        comparativo_anios = inicial
        #FIXME: no longer? comparativo_anios = list(chain(inicial, final, ))

        # obtiene datos para OIM comparativo de un año específico
        inicial = list(IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio, ingreso__anio=year, ingreso__periodo=PERIODO_INICIAL).values('ingreso__periodo').annotate(municipio=Sum('asignado')))
        actualizado = list(IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio, ingreso__anio=year, ingreso__periodo=PERIODO_ACTUALIZADO).values('ingreso__periodo').annotate(municipio=Sum('asignado')))
        final = list(IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio, ingreso__anio=year, ingreso__periodo=PERIODO_FINAL).values('ingreso__periodo').annotate(municipio=Sum('ejecutado')))

        # obtiene datos para municipio de la misma clase
        inicial_clase = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_INICIAL,\
                ingreso__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, ingreso__municipio__clase__anio=year).\
                values('ingreso__periodo').order_by('ingreso__periodo').annotate(clase=Sum('asignado'))
        actualizado_clase = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_ACTUALIZADO,\
                ingreso__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, ingreso__municipio__clase__anio=year).\
                values('ingreso__periodo').order_by('ingreso__periodo').annotate(clase=Sum('asignado'))
        final_clase = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_FINAL,\
                ingreso__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, ingreso__municipio__clase__anio=year).\
                values('ingreso__periodo').order_by('ingreso__periodo').annotate(clase=Sum('ejecutado'))

        # inserta datos para municipio de la misma clase
        if inicial:
            inicial[0]['clase'] = inicial_clase[0]['clase'] / mi_clase_count
        if actualizado:
            actualizado[0]['clase'] = actualizado_clase[0]['clase'] / mi_clase_count
        if final:
            final[0]['clase'] = final_clase[0]['clase'] / mi_clase_count
        comparativo3 = list(chain(inicial, actualizado, final))
        comparativo2 = list(chain(inicial, final, ))
        for d in comparativo3:
            d.update((k, PERIODO_VERBOSE[v]) for k, v in d.iteritems() if k == "ingreso__periodo")

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

        source = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=periodo).values('subsubtipoingreso__origen__nombre').order_by('subsubtipoingreso__origen__nombre').annotate(**{quesumar: Sum(quesumar) })
        tipos_inicial = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_INICIAL).values('subsubtipoingreso__origen__nombre').annotate(asignado=Sum('asignado')).order_by('subsubtipoingreso__origen__nombre')
        tipos_final = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=periodo).values('subsubtipoingreso__origen__nombre').annotate(ejecutado=Sum('ejecutado')).order_by('subsubtipoingreso__origen__nombre')
        sources = glue(tipos_inicial, tipos_final, 'subsubtipoingreso__origen__nombre')
        source_barra = IngresoDetalle.objects.filter(ingreso__periodo=periodo)
        source_barra2 = IngresoDetalle.objects.filter(ingreso__periodo=periodo, ingreso__anio__gt=year_list[-3])

        # obtiene datos de ingresos en ditintos rubros
        rubrosp_inicial = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_INICIAL, \
                subsubtipoingreso__origen=OrigenRecurso.RECAUDACION,).\
                values('subtipoingreso__codigo','subtipoingreso__nombre').order_by('subtipoingreso__codigo').annotate(inicial_asignado=Sum('asignado'))
        rubrosp_actualizado = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_ACTUALIZADO, \
                subsubtipoingreso__origen=OrigenRecurso.RECAUDACION,).\
                values('subtipoingreso__codigo','subtipoingreso__nombre').order_by('subtipoingreso__codigo').annotate(actualizado_asignado=Sum('asignado'), actualizado_ejecutado=Sum('ejecutado'))
        rubrosp_final = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_FINAL, \
                subsubtipoingreso__origen=OrigenRecurso.RECAUDACION,).\
                values('subtipoingreso__codigo','subtipoingreso__nombre').order_by('subtipoingreso__codigo').annotate(final_asignado=Sum('asignado'), final_ejecutado=Sum('ejecutado'))
        rubrosp_periodo = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=periodo, \
                subsubtipoingreso__origen=OrigenRecurso.RECAUDACION,).\
                values('subtipoingreso__codigo','subtipoingreso__nombre').order_by('subtipoingreso__codigo').annotate(ejecutado=Sum('ejecutado'))
        rubrosp = superglue(data=(rubrosp_inicial, rubrosp_final, rubrosp_actualizado, rubrosp_periodo), key='subtipoingreso__codigo')

        # obtiene datos de ingresos en ditintos rubros
        rubros_inicial = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_INICIAL, ).\
                values('subsubtipoingreso__origen__id','subsubtipoingreso__origen__nombre').order_by('subsubtipoingreso__origen__id').annotate(inicial_asignado=Sum('asignado'))
        rubros_actualizado = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_ACTUALIZADO, ).\
                values('subsubtipoingreso__origen__id','subsubtipoingreso__origen__nombre').order_by('subsubtipoingreso__origen__id').annotate(actualizado_asignado=Sum('asignado'), actualizado_ejecutado=Sum('ejecutado'))
        rubros_final= IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_FINAL, ).\
                values('subsubtipoingreso__origen__id','subsubtipoingreso__origen__nombre').order_by('subsubtipoingreso__origen__id').annotate(final_asignado=Sum('asignado'), final_ejecutado=Sum('ejecutado'))
        rubros_periodo = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=periodo, ).\
                    values('subsubtipoingreso__origen__id','subsubtipoingreso__origen__nombre').order_by('subsubtipoingreso__origen__id').annotate(ejecutado=Sum('ejecutado'))
        rubros = superglue(data=(rubros_inicial, rubros_final, rubros_actualizado, rubros_periodo), key='subsubtipoingreso__origen__id')

        source_inicial = IngresoDetalle.objects.filter(ingreso__periodo=PERIODO_INICIAL,).\
            values('ingreso__anio').order_by('ingreso__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_final = IngresoDetalle.objects.filter(ingreso__periodo=PERIODO_FINAL,).\
            values('ingreso__anio').order_by('ingreso__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_periodo = IngresoDetalle.objects.filter(ingreso__periodo=periodo,).\
            values('ingreso__anio').order_by('ingreso__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

        # grafico de ejecutado y asignado a nivel nacional (distintas clases)
        sql_tpl="SELECT clasificacion,\
                (SELECT SUM({quesumar}) FROM core_IngresoDetalle JOIN core_Ingreso ON core_IngresoDetalle.ingreso_id=core_Ingreso.id JOIN core_TipoIngreso ON core_IngresoDetalle.tipoingreso_id=core_TipoIngreso.codigo \
                JOIN lugar_clasificacionmunicano ON core_Ingreso.municipio_id=lugar_clasificacionmunicano.municipio_id AND core_Ingreso.anio=lugar_clasificacionmunicano.anio \
                WHERE core_Ingreso.anio={year} AND core_Ingreso.periodo='{periodo}' AND lugar_clasificacionmunicano.clasificacion_id=clase.id ) \
                AS {quesumar} FROM lugar_clasificacionmunic AS clase ORDER BY clasificacion"
        sql = sql_tpl.format(quesumar="asignado", year=year, periodo=PERIODO_INICIAL,)
        cursor = connection.cursor()
        cursor.execute(sql)
        inicial = dictfetchall(cursor)
        sql = sql_tpl.format(quesumar="ejecutado", year=year, periodo=PERIODO_FINAL,)
        cursor = connection.cursor()
        cursor.execute(sql)
        final = dictfetchall(cursor)
        sql = sql_tpl.format(quesumar="asignado", year=year, periodo=PERIODO_ACTUALIZADO,)
        cursor = connection.cursor()
        cursor.execute(sql)
        actualizado = dictfetchall(cursor)
        porclase = glue(inicial, final, 'clasificacion', actualizado=actualizado)
        for d in porclase:
            if d['actualizado'] and d['asignado']:
                # FIXME: asignado?
                d['nivel'] = d['asignado'] / d['actualizado'] * 100
            else:
                d['nivel'] = 0

        # grafico de ejecutado y asignado a nivel nacional (distintas clases) porcentage
        sql_tpl="SELECT clasificacion,\
                (SELECT SUM({quesumar}) FROM core_IngresoDetalle JOIN core_Ingreso ON core_IngresoDetalle.ingreso_id=core_Ingreso.id JOIN core_TipoIngreso ON core_IngresoDetalle.tipoingreso_id=core_TipoIngreso.codigo \
                JOIN lugar_clasificacionmunicano ON core_Ingreso.municipio_id=lugar_clasificacionmunicano.municipio_id AND core_Ingreso.anio=lugar_clasificacionmunicano.anio \
                WHERE core_Ingreso.anio={year} AND core_Ingreso.periodo='{periodo}' AND lugar_clasificacionmunicano.clasificacion_id=clase.id) /\
                (SELECT SUM(poblacion) FROM lugar_Poblacion \
                JOIN lugar_clasificacionmunicano ON lugar_Poblacion.municipio_id = lugar_clasificacionmunicano.municipio_id \
                JOIN lugar_clasificacionmunic ON lugar_clasificacionmunicano.clasificacion_id=lugar_clasificacionmunic.id \
                WHERE lugar_Poblacion.anio={year} AND lugar_clasificacionmunic.clasificacion=clase.clasificacion)\
                AS {quesumar} FROM lugar_clasificacionmunic AS clase ORDER BY clasificacion"
        sql = sql_tpl.format(quesumar="asignado", year=year, periodo=PERIODO_INICIAL,)
        cursor = connection.cursor()
        cursor.execute(sql)
        inicial = dictfetchall(cursor)
        sql = sql_tpl.format(quesumar="ejecutado", year=year, periodo=periodo,)
        cursor = connection.cursor()
        cursor.execute(sql)
        final = dictfetchall(cursor)
        sql = sql_tpl.format(quesumar="asignado", year=year, periodo=PERIODO_ACTUALIZADO,)
        cursor = connection.cursor()
        cursor.execute(sql)
        actualizado = dictfetchall(cursor)
        porclasep = glue(inicial, final, 'clasificacion', actualizado=actualizado)

        # obtiene datos para OIM comparativo de un año específico
        inicial = list(IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_INICIAL).values('ingreso__periodo').annotate(monto=Sum('asignado')).order_by('ingreso__periodo'))
        actualizado = list(IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_ACTUALIZADO).values('ingreso__periodo').annotate(monto=Sum('asignado')).order_by('ingreso__periodo'))
        final = list(IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_FINAL).values('ingreso__periodo').annotate(monto=Sum('ejecutado')).order_by('ingreso__periodo'))
        comparativo2 = list(chain(inicial, final, ))
        comparativo3 = list(chain(inicial, final, actualizado))
        for d in comparativo3:
            d.update((k, PERIODO_VERBOSE[v]) for k, v in d.iteritems() if k == "ingreso__periodo")

        # obtiene datos para grafico comparativo de tipo de ingresos
        tipo_inicial= list(IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_INICIAL).values('subsubtipoingreso__origen__nombre').order_by('subsubtipoingreso__origen__nombre').annotate(asignado=Sum('asignado')))
        tipo_final = list(IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=PERIODO_FINAL).values('subsubtipoingreso__origen__nombre').order_by('subsubtipoingreso__origen__nombre').annotate(ejecutado=Sum('ejecutado')))
        tipo = glue(tipo_inicial, tipo_final, 'subsubtipoingreso__origen__nombre')

        # obtiene datos para OIM comparativo de todos los años
        anios_inicial = list(IngresoDetalle.objects.filter(ingreso__periodo=PERIODO_INICIAL).values('ingreso__anio', 'ingreso__periodo').order_by('ingreso__anio', 'ingreso__periodo').annotate(asignado=Sum('asignado')))
        anios_final = list(IngresoDetalle.objects.filter(ingreso__periodo=PERIODO_FINAL).values('ingreso__anio', 'ingreso__periodo').order_by('ingreso__anio', 'ingreso__periodo').annotate(ejecutado=Sum('ejecutado')))
        comparativo_anios = glue(anios_inicial, anios_final, 'ingreso__anio')

        # obtiene valores para este año de las listas
        try:
            asignado = (item for item in source_inicial if item["ingreso__anio"] == int(year)).next()['asignado']
        except StopIteration:
            asignado = 0
        try:
            ejecutado = (item for item in source_periodo if item["ingreso__anio"] == int(year)).next()['ejecutado']
        except StopIteration:
            ejecutado = 0
        # FIXME que es esto: ???
        source_anios = glue(source_inicial, source_final, 'ingreso__anio')


    #
    # chartit!
    #
    if municipio:
        oim_comparativo_anios = RawDataPool(
            series=
                [{'options': {'source': comparativo_anios },
                'names':  ['Ejecucion presupuestaria','Periodo','P.Inicial',u'Municipio P. Final',u'Categoria P.Inicial',u'Categoria P. Final'],
                'terms':  ['ingreso__anio','ingreso__periodo','municipio_inicial','municipio_final','clase_inicial','clase_final'],
                }],
            )
        oim_comparativo2 = RawDataPool(
            series=
                [{'options': {'source': comparativo2 },
                'names':  [u'Ingreso',u'Mi municipio',u'Categoría %s' % (mi_clase.clasificacion,)],
                'terms':  ['ingreso__periodo','municipio','clase'],
                }],
                #sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
                )
        oim_comparativo3 = RawDataPool(
            series=
                [{'options': {'source': comparativo3 },
                'names':  ['Modificaciones al presupuesto',u'Mi Municipio',u'Categoria %s' % (mi_clase.clasificacion,)],
                'terms':  ['ingreso__periodo','municipio','clase'],
                }],
                #sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
                )
        oim_comparativo_anios_column = Chart(
                datasource = oim_comparativo_anios,
                series_options =
                [{'options':{
                    'type': 'column',
                    'stacking': False},
                    'names':  ['Mi Municipio Inicial',u'Categoria P. Inicial',u'Mi Municipio P.Final',u'Categoria %s' % (mi_clase.clasificacion,)],
                    'terms':{
                    'ingreso__anio': ['municipio_inicial', 'clase_inicial', 'municipio_final', 'clase_final'],
                    },
                    }],
                chart_options =
                {'title': { 'text': ' '}},
                )
        oim_comparativo2_column = Chart(
                datasource = oim_comparativo2,
                series_options =
                [{'options':{
                    'type': 'column',
                    'stacking': False},
                    'terms':{
                    'ingreso__periodo': ['municipio', 'clase']
                    },
                    }],
                chart_options =
                {'title': { 'text': ' '},
                 'yAxis': { 'title': {'text': u'Millones de córdobas'} },
                },
                )
        oim_comparativo3_column = Chart(
                datasource = oim_comparativo3,
                series_options =
                [{'options':{
                    'type': 'column',
                    'stacking': False},
                    'names':  [u'Municipio',u'Categoria'],
                    'terms':{
                    'ingreso__periodo': ['municipio','clase']
                    },
                }],
                chart_options =
                {'title': { 'text': ' '}},
                )

    else: # no municipio chartit
        oim_comparativo_anios = RawDataPool(
            series=
                [{'options': {'source': comparativo_anios },
                'names':  ['Ejecucion presupuestaria','Periodo','Asignado',u'Ejecutado'],
                'terms':  ['ingreso__anio','ingreso__periodo','asignado','ejecutado',],
                }],
            )
        oim_comparativo2 = RawDataPool(
            series=
                [{'options': {'source': comparativo2 },
                'names':  [u'Ingreso',u'Ingresos del periodo'],
                'terms':  ['ingreso__periodo', 'monto'],
                }],
                )
        oim_comparativo3 = RawDataPool(
            series=
                [{'options': {'source': comparativo3 },
                'names':  [' ','Ingresos totales'],
                'terms':  ['ingreso__periodo', 'monto'],
                }],
                )
        oim_comparativo2_column = Chart(
                datasource = oim_comparativo2,
                series_options =
                [{'options':{
                    'type': 'column',
                    'stacking': False},
                    'terms':{
                    'ingreso__periodo': ['monto',]
                    },
                    }],
                chart_options = {
                    'title': { 'text': ' '},
                    #'subtitle': { 'text': u'Municipio de %s y Categoría del Municipio %s' % (municipio_row.nombre, year)},
                    'yAxis': { 'title': {'text': u'Millones de córdobas'} },
                },
                )
        oim_comparativo3_column = Chart(
                datasource = oim_comparativo3,
                series_options =
                [{'options':{
                    'type': 'column',
                    'stacking': False},
                    'terms':{
                    'ingreso__periodo': ['monto', ]
                    },
                    }],
                chart_options =
                {'title': { 'text': ' '}},
                )
        oim_comparativo_anios_column = Chart(
                datasource = oim_comparativo_anios,
                series_options =
                [{'options':{
                    'type': 'column',
                    'stacking': False},
                    'terms':{
                    'ingreso__anio': ['ejecutado', 'asignado'],
                    },
                    }],
                chart_options =
                {'title': { 'text': ' '}},
                )

    oim_tipo = RawDataPool(
        series=
            [{'options': {'source': tipo },
            'terms':  ['subsubtipoingreso__origen__nombre','ejecutado','asignado'],
            }],
        )
    oim_tipo_column = Chart(
            datasource = oim_tipo,
            series_options =
            [{'options':{
                'type': 'column',
                'stacking': False},
                'terms':{
                'subsubtipoingreso__origen__nombre': ['ejecutado', 'asignado'],
                },
                }],
            chart_options =
            {
                'title': { 'text': ' '},
                'data': { 'table': 'datatable'},
            },
    )
    oimdata_barra = PivotDataPool(
           series=
            [{'options': {'source': source_barra,
                        'categories': 'ingreso__anio',
                        'legend_by': 'subsubtipoingreso__origen__nombre', },
              'terms': {
                  'ejecutado':Sum('ejecutado'),
                  'asignado':Sum('asignado'),
                }
              }],
            #sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
            )
    asignado_barra = PivotChart(
            datasource = oimdata_barra,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': 'percent'},
                'terms':['asignado']
                }],
            chart_options =
              {'title': { 'text': 'Ingresos asignados por origen %s' % (municipio,)}},
            )
    oimdata_barra2 = PivotDataPool(
           series=
            [{'options': {'source': source_barra2,
                        'categories': 'ingreso__anio',
                         },
              'terms': {
                  'ejecutado':Sum('ejecutado'),
                  'asignado':Sum('asignado'),
                }
              }],
            )
    barra = PivotChart(
            datasource = oimdata_barra2,
            series_options =
              [{'options':{
                  'type': 'column',
                },
                'terms':['asignado','ejecutado']
                }],
            chart_options =
              {'title': { 'text': 'Ingresos por periodo %s' % (municipio,)}},
            )

    oimdata = DataPool(
           series=
            [{'options': {'source': source },
              'terms': [
                'subsubtipoingreso__origen__nombre',
                quesumar,
                ]}
             ])

    asignado_pie = Chart(
            datasource = oimdata,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'subsubtipoingreso__origen__nombre': [
                    quesumar]
                  }}],
            chart_options =
              {
                  'title': {'text': 'Ingresos %s %s %s' % (quesumar, municipio, year,)},
                  'plotOptions': { 'pie': { 'dataLabels': { 'enabled': True, 'format': '{point.percentage:.1f} %' }, 'showInLegend': True, 'depth': 35}},
                  'options3d': { 'enabled': 'true',  'alpha': '45', 'beta': '0' },
                  'tooltip': { 'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>' },
              })

    ejecutado_pie = Chart(
            datasource = oimdata,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'subsubtipoingreso__origen__nombre': [
                    quesumar]
                  }}],
            chart_options =
              {
                  'options3d': { 'enabled': 'true',  'alpha': '45', 'beta': '0' },
                  'title': {'text': ' '},
                  'plotOptions': { 'pie': { 'dataLabels': { 'enabled': True, 'format': '{point.percentage:.1f} %' }, 'showInLegend': True, 'depth': 35, }},
                  'tooltip': { 'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>' },
              }
    )

    # tabla: get total and percent
    total = {}
    total['ejecutado'] = sum(item['ejecutado'] for item in sources)
    total['asignado'] = sum(item['asignado'] for item in sources)
    for row in sources:
        row['ejecutado_percent'] = round(row['ejecutado'] / total['ejecutado'] * 100, 1) if total['ejecutado'] > 0 else 0
        row['asignado_percent'] = round(row['asignado'] / total['asignado'] * 100, 1) if total['asignado'] > 0 else 0

    # tabla: get ingresos por año
    if municipio:
        source_cuadro = IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio)
    else:
        source_cuadro = IngresoDetalle.objects.all()
    porano_table = {}
    ys = source_cuadro.order_by('subsubtipoingreso__origen__nombre').values('subsubtipoingreso__origen__nombre').distinct()
    for y in ys:
        label = y['subsubtipoingreso__origen__nombre']
        porano_table[label] = {}
        for ayear in year_list:
            periodo = Anio.objects.get(anio=ayear).periodo
            quesumar = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'
            value = source_cuadro.filter(ingreso__anio=ayear, ingreso__periodo=periodo, subsubtipoingreso__origen__nombre=label).aggregate(total=Sum(quesumar))['total']
            porano_table[label][ayear] = value if value else ''
        if municipio and year:
            periodo = PERIODO_FINAL
            quesumar = 'ejecutado'
            value = IngresoDetalle.objects.filter(ingreso__anio=year, ingreso__periodo=periodo, subsubtipoingreso__origen__nombre=label, \
                    ingreso__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, ingreso__municipio__clase__anio=year).\
                    aggregate(total=Sum(quesumar))['total']
            if value:
                value = value / mi_clase_count
            porano_table[label]['extra'] = value if value else '...'

    if portada:
        charts =  (ejecutado_pie, )
    elif municipio:
        charts =  (ejecutado_pie, oim_comparativo_anios_column, oim_comparativo2_column, oim_comparativo3_column, oim_tipo_column, asignado_barra, barra, )
    else:
        charts =  (ejecutado_pie, oim_comparativo_anios_column, oim_comparativo2_column, oim_comparativo3_column, oim_tipo_column, asignado_barra, barra, )

    return {'charts': charts, \
            'year_data': year_data, \
            'mi_clase': mi_clase, 'municipio': municipio_row, 'year': year, 'porano': porano_table, 'totales': sources, \
            'ejecutado': ejecutado, 'asignado': asignado, 'year_list': year_list, 'municipio_list': municipio_list, \
            'anuales': anual2, 'porclase': porclase, 'porclasep': porclasep, 'rubros': rubros, 'rubrosp': rubrosp, 'otros': otros}
