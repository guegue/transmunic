# -*- coding: utf-8 -*-
##############################################################################
#
# OGM charts /core/ogm
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

from core.models import GastoDetalle, Gasto, GastoDetalle, Gasto, Inversion, Proyecto, Municipio, TipoGasto, InversionFuente, InversionFuenteDetalle, CatInversion, ClasificacionMunicAno
from core.models import Anio, getYears, dictfetchall, glue
from core.models import PERIODO_INICIAL, PERIODO_ACTUALIZADO, PERIODO_FINAL, PERIODO_VERBOSE
from lugar.models import Poblacion

def ogm_chart(municipio=None, year=None, portada=False):
    municipio_list = Municipio.objects.all()
    year_list = getYears(Gasto)
    if not year:
        year = year_list[-1]

    periodo = Anio.objects.get(anio=year).periodo
    quesumar = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'

    ChartError = False

    if municipio:
        porclase = None
        porclasep = None
        municipio_row = Municipio.objects.get(slug=municipio)
        municipio_id = municipio_row.id
        municipio_nombre = municipio_row.nombre

        source = GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__anio=year).values('subsubtipogasto__origen__nombre').annotate(ejecutado=Sum(quesumar)).order_by('subsubtipogasto__origen__nombre')
        tipos_inicial = GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__anio=year).values('subsubtipogasto__origen__nombre').annotate(asignado=Sum('asignado')).order_by('subsubtipogasto__origen__nombre')
        tipos_final = GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__anio=year).values('subsubtipogasto__origen__nombre').annotate(ejecutado=Sum('ejecutado')).order_by('subsubtipogasto__origen__nombre')
        sources = glue(tipos_inicial, tipos_final, periodo, 'subsubtipogasto__origen__nombre')
        source_barra = GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=periodo, gasto__anio__gt=year_list[-3])
        source_pivot = GastoDetalle.objects.filter(gasto__periodo=periodo, gasto__municipio__slug=municipio)

        source_inicial = GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL, \
            gasto__municipio__slug=municipio).\
            values('gasto__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_final = GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL, \
            gasto__municipio__slug=municipio).\
            values('gasto__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        # obtiene valores para este año de las listas
        try:
            asignado = (item for item in source_inicial if item["gasto__anio"] == int(year)).next()['asignado']
        except StopIteration:
            asignado = 0
        try:
            ejecutado = (item for item in source_final if item["gasto__anio"] == int(year)).next()['ejecutado']
        except StopIteration:
            ejecutado = 0

        # obtiene datos de gastos en ditintos rubros de persoal pemanente (codigo 1100000)
        rubrosp_inicial = GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL, \
                subtipogasto=TipoGasto.PERSONAL_PERMANENTE,).\
                values('subsubtipogasto__codigo','subsubtipogasto__nombre').order_by('subsubtipogasto__codigo').annotate(asignado=Sum('asignado'))
        rubrosp_actualizado = GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio, gasto__periodo=PERIODO_ACTUALIZADO, \
                subtipogasto=TipoGasto.PERSONAL_PERMANENTE,).\
                values('subsubtipogasto__codigo','subsubtipogasto__nombre').order_by('subsubtipogasto__codigo').annotate(ejecutado=Sum('ejecutado'))
        rubrosp_final= GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio, gasto__periodo=PERIODO_FINAL, \
                subtipogasto=TipoGasto.PERSONAL_PERMANENTE,).\
                values('subsubtipogasto__codigo','subsubtipogasto__nombre').order_by('subsubtipogasto__codigo').annotate(ejecutado=Sum('ejecutado'))
        rubrosp = glue(rubrosp_inicial, rubrosp_final, periodo, 'subsubtipogasto__codigo', actualizado=rubrosp_actualizado)

        # obtiene datos de gastos en ditintos rubros de corriente (clasificacion 0)
        rubros_inicial = GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL,).\
                values('tipogasto__codigo','tipogasto__nombre').order_by('tipogasto__codigo').annotate(asignado=Sum('asignado'))
        rubros_actualizado = GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio, gasto__periodo=PERIODO_ACTUALIZADO,).\
                values('tipogasto__codigo','tipogasto__nombre').order_by('tipogasto__codigo').annotate(ejecutado=Sum('ejecutado'))
        rubros_final= GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio, gasto__periodo=PERIODO_FINAL,).\
                values('tipogasto__codigo','tipogasto__nombre').order_by('tipogasto__codigo').annotate(ejecutado=Sum('ejecutado'))
        rubros = glue(rubros_inicial, rubros_final, periodo, 'tipogasto__codigo', actualizado=rubros_actualizado)

        # obtiene clase y contador (otros en misma clase) para este año
        mi_clase = ClasificacionMunicAno.objects.get(municipio__slug=municipio, anio=year)
        mi_clase_count = ClasificacionMunicAno.objects.filter(clasificacion__clasificacion=mi_clase.clasificacion, anio=year).count()
        # obtiene clase y contador (otros en misma clase) para todos los años
        mi_clase_anios = list(ClasificacionMunicAno.objects.filter(municipio__slug=municipio).values('anio', 'clasificacion__clasificacion').annotate())
        mi_clase_anios_count = {}
        for aclase in mi_clase_anios:
            mi_clase_anios_count[aclase['anio']] = ClasificacionMunicAno.objects.filter(clasificacion__clasificacion=aclase['clasificacion__clasificacion'], anio=aclase['anio']).count()

        # obtiene datos de municipios de la misma clase
        municipios_inicial = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_INICIAL, gasto__municipio__clase__anio=year, \
                gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion).\
                values('gasto__municipio__nombre', 'gasto__municipio__slug').order_by('gasto__municipio__nombre').annotate(asignado=Sum('asignado'))
        municipios_actualizado = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_ACTUALIZADO, gasto__municipio__clase__anio=year, \
                gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion).\
                values('gasto__municipio__nombre', 'gasto__municipio__slug').order_by('gasto__municipio__nombre').annotate(ejecutado=Sum('ejecutado'))
        municipios_final = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_FINAL, gasto__municipio__clase__anio=year, \
                gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion).\
                values('gasto__municipio__nombre', 'gasto__municipio__slug').order_by('gasto__municipio__nombre').annotate(ejecutado=Sum('ejecutado'))
        otros = glue(municipios_inicial, municipios_final, PERIODO_FINAL, 'gasto__municipio__nombre', actualizado=municipios_actualizado)
        # inserta porcentages de total de gastos
        for row in otros:
            total_poblacion = Poblacion.objects.filter(anio=year, municipio__clasificaciones__clasificacion=mi_clase.clasificacion)\
                    .aggregate(poblacion=Sum('poblacion'))['poblacion']
            row['ejecutado_percent'] = round(row['ejecutado'] / total_poblacion * 100, 0) if total_poblacion > 0 else 0
            row['asignado_percent'] = round(row['asignado'] / total_poblacion * 100, 0) if total_poblacion > 0 else 0
        otros = sorted(otros, key=itemgetter('ejecutado_percent'), reverse=True)

        # obtiene datos para grafico comparativo de tipo de gastos
        tipo_inicial= list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__anio=year, gasto__periodo=PERIODO_INICIAL).values('subsubtipogasto__origen__nombre').annotate(asignado=Sum('asignado')))
        tipo_final = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__anio=year, gasto__periodo=PERIODO_FINAL).values('subsubtipogasto__origen__nombre').annotate(ejecutado=Sum('ejecutado')))
        tipo = glue(tipo_inicial, tipo_final, periodo, 'subsubtipogasto__origen__nombre')

        # obtiene datos comparativo de todos los años FIXME: replaces data below?
        inicial = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL).values('gasto__anio', 'gasto__periodo').annotate(asignado=Sum('asignado')))
        final = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_FINAL).values('gasto__anio', 'gasto__periodo').annotate(ejecutado=Sum('ejecutado')))
        anual2 = glue(inicial=inicial, final=final, periodo=PERIODO_INICIAL, campo='gasto__anio')
        final_clase_sql = "SELECT core_gasto.anio AS gasto__anio,'F' AS gasto__periodo,SUM(ejecutado) AS clase_final FROM core_gastodetalle JOIN core_gasto ON core_gastodetalle.gasto_id=core_gasto.id \
        JOIN lugar_clasificacionmunicano ON core_gasto.municipio_id=lugar_clasificacionmunicano.municipio_id AND \
        core_gasto.anio=lugar_clasificacionmunicano.anio JOIN core_tipogasto ON core_gastodetalle.tipogasto_id=core_tipogasto.codigo \
        WHERE core_gasto.periodo=%s \
        AND lugar_clasificacionmunicano.clasificacion_id=(SELECT clasificacion_id FROM lugar_clasificacionmunicano WHERE municipio_id=%s AND lugar_clasificacionmunicano.anio=core_gasto.anio) \
        GROUP BY core_gasto.anio"
        cursor = connection.cursor()
        cursor.execute(final_clase_sql, [PERIODO_FINAL, municipio_id])
        final_clase = dictfetchall(cursor)
        for row in anual2:
            found = False
            for row2 in final_clase:
                if row2['gasto__anio'] == row['gasto__anio']:
                    found = True
                    try:
                        row['clase_final'] = row2['clase_final'] / mi_clase_anios_count[row['gasto__anio']]
                    except KeyError:
                        row['clase_final'] = 0
            if not found:
                row['clase_final'] = 0
        comparativo_anios = anual2

        # obtiene datos para OGM comparativo de todos los años
        inicial = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL).values('gasto__anio', 'gasto__periodo').annotate(municipio_inicial=Sum('asignado')))
        final = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_FINAL).values('gasto__anio', 'gasto__periodo').annotate(municipio_final=Sum('ejecutado')))
        # obtiene datos para municipio de la misma clase de todos los años
        inicial_clase_sql = "SELECT core_gasto.anio AS gasto__anio,SUM(asignado) AS clase_inicial FROM core_gastodetalle JOIN core_gasto ON core_gastodetalle.gasto_id=core_gasto.id \
        JOIN lugar_clasificacionmunicano ON core_gasto.municipio_id=lugar_clasificacionmunicano.municipio_id AND \
        core_gasto.anio=lugar_clasificacionmunicano.anio WHERE core_gasto.periodo=%s \
        AND lugar_clasificacionmunicano.clasificacion_id=(SELECT clasificacion_id FROM lugar_clasificacionmunicano WHERE municipio_id=%s AND lugar_clasificacionmunicano.anio=core_gasto.anio) \
        GROUP BY core_gasto.anio"
        cursor = connection.cursor()
        cursor.execute(inicial_clase_sql, [PERIODO_INICIAL, municipio_id])
        inicial_clase = dictfetchall(cursor)
        final_clase_sql = "SELECT core_gasto.anio AS gasto__anio,SUM(ejecutado) AS clase_final FROM core_gastodetalle JOIN core_gasto ON core_gastodetalle.gasto_id=core_gasto.id \
        JOIN lugar_clasificacionmunicano ON core_gasto.municipio_id=lugar_clasificacionmunicano.municipio_id AND \
        core_gasto.anio=lugar_clasificacionmunicano.anio WHERE core_gasto.periodo=%s \
        AND lugar_clasificacionmunicano.clasificacion_id=(SELECT clasificacion_id FROM lugar_clasificacionmunicano WHERE municipio_id=%s AND lugar_clasificacionmunicano.anio=core_gasto.anio) \
        GROUP BY core_gasto.anio"
        cursor = connection.cursor()
        cursor.execute(final_clase_sql, [PERIODO_FINAL, municipio_id])
        final_clase = dictfetchall(cursor)

        # inserta datos para municipio de la misma clase
        for row in inicial:
            for row2 in inicial_clase:
                if row2['gasto__anio'] == row['gasto__anio']:
                    row['clase_inicial'] = row2['clase_inicial'] / mi_clase_anios_count[row['gasto__anio']]
        for row in final:
            for row2 in final_clase:
                if row2['gasto__anio'] == row['gasto__anio']:
                    row['clase_final'] = row2['clase_final'] / mi_clase_anios_count[row['gasto__anio']]
        for row in inicial:
            found = False
            for row2 in final:
                if row2['gasto__anio'] == row['gasto__anio']:
                    found = True
                    row['clase_final'] = row2['clase_final']
                    row['municipio_final'] = row2['municipio_final']
                if not found:
                    row['clase_final'] = 0
                    row['municipio_final'] = 0
        comparativo_anios = inicial
        #FIXME: no longer? comparativo_anios = list(chain(inicial, final, ))

        # obtiene datos para OGM comparativo de un año específico
        inicial = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__anio=year, gasto__periodo=PERIODO_INICIAL).values('gasto__periodo').annotate(municipio=Sum('asignado')))
        actualizado = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__anio=year, gasto__periodo=PERIODO_ACTUALIZADO).values('gasto__periodo').annotate(municipio=Sum('ejecutado')))
        final = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__anio=year, gasto__periodo=PERIODO_FINAL).values('gasto__periodo').annotate(municipio=Sum('ejecutado')))

        # obtiene datos para municipio de la misma clase
        inicial_clase = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_INICIAL,\
                gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, gasto__municipio__clase__anio=year).\
                values('gasto__periodo').order_by('gasto__periodo').annotate(clase=Sum('asignado'))
        actualizado_clase = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_ACTUALIZADO,\
                gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, gasto__municipio__clase__anio=year).\
                values('gasto__periodo').order_by('gasto__periodo').annotate(clase=Sum('ejecutado'))
        final_clase = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_FINAL,\
                gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, gasto__municipio__clase__anio=year).\
                values('gasto__periodo').order_by('gasto__periodo').annotate(clase=Sum('ejecutado'))

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
            d.update((k, PERIODO_VERBOSE[v]) for k, v in d.iteritems() if k == "gasto__periodo")
    else:
        #
        # no municipio
        #
        otros = None
        mi_clase = None
        municipio_row = ''
        municipio = ''

        # obtiene datos comparativo de todos los años
        inicial = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL, tipogasto__clasificacion=TipoGasto.CORRIENTE,).values('gasto__anio', 'gasto__periodo').annotate(asignado=Sum('asignado')))
        final = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL, tipogasto__clasificacion=TipoGasto.CORRIENTE,).values('gasto__anio', 'gasto__periodo').annotate(ejecutado=Sum('ejecutado')))
        anual2 = glue(inicial=inicial, final=final, periodo=PERIODO_INICIAL, campo='gasto__anio')

        source = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=periodo).values('subsubtipogasto__origen__nombre').annotate(ejecutado=Sum(quesumar)).order_by('subsubtipogasto__origen__nombre')
        tipos_inicial = GastoDetalle.objects.filter(gasto__anio=year).values('subsubtipogasto__origen__nombre').annotate(asignado=Sum('asignado')).order_by('subsubtipogasto__origen__nombre')
        tipos_final = GastoDetalle.objects.filter(gasto__anio=year).values('subsubtipogasto__origen__nombre').annotate(ejecutado=Sum('ejecutado')).order_by('subsubtipogasto__origen__nombre')
        sources = glue(tipos_inicial, tipos_final, periodo, 'subsubtipogasto__origen__nombre')
        source_barra = GastoDetalle.objects.filter(gasto__periodo=periodo, gasto__anio__gt=year_list[-3])
        source_pivot = GastoDetalle.objects.filter(gasto__periodo=periodo)

        source = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=periodo).values('subsubtipogasto__origen__nombre').annotate(ejecutado=Sum(quesumar)).order_by('subsubtipogasto__origen')
        source_barra = GastoDetalle.objects.filter(gasto__periodo=periodo)
        source_barra2 = GastoDetalle.objects.filter(gasto__periodo=periodo, gasto__anio__gt=year_list[-3])
        
        # obtiene datos de gastos en ditintos rubros
        rubrosp_inicial = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_INICIAL, \
                subtipogasto=TipoGasto.PERSONAL_PERMANENTE,).\
                exclude(tipogasto__codigo=TipoGasto.IMPREVISTOS).\
                values('subsubtipogasto__codigo','subsubtipogasto__nombre').order_by('subsubtipogasto__codigo').annotate(asignado=Sum('asignado'))
        rubrosp_actualizado = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_ACTUALIZADO, \
                subtipogasto=TipoGasto.PERSONAL_PERMANENTE,).\
                exclude(tipogasto__codigo=TipoGasto.IMPREVISTOS).\
                values('subsubtipogasto__codigo','subsubtipogasto__nombre').order_by('subsubtipogasto__codigo').annotate(ejecutado=Sum('ejecutado'))
        rubrosp_final= GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_FINAL, \
                subtipogasto=TipoGasto.PERSONAL_PERMANENTE,).\
                exclude(tipogasto__codigo=TipoGasto.IMPREVISTOS).\
                values('subsubtipogasto__codigo','subsubtipogasto__nombre').order_by('subsubtipogasto__codigo').annotate(ejecutado=Sum('ejecutado'))
        rubrosp = glue(rubrosp_inicial, rubrosp_final, periodo, 'subsubtipogasto__codigo', actualizado=rubrosp_actualizado)

        # obtiene datos de gastos en ditintos rubros
        rubros_inicial = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_INICIAL, ).\
                exclude(tipogasto__codigo=TipoGasto.IMPREVISTOS).\
                values('tipogasto__codigo','tipogasto__nombre').order_by('tipogasto__codigo').annotate(asignado=Sum('asignado'))
        rubros_actualizado = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_ACTUALIZADO, ).\
                exclude(tipogasto__codigo=TipoGasto.IMPREVISTOS).\
                values('tipogasto__codigo','tipogasto__nombre').order_by('tipogasto__codigo').annotate(ejecutado=Sum('ejecutado'))
        rubros_final= GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_FINAL, ).\
                exclude(tipogasto__codigo=TipoGasto.IMPREVISTOS).\
                values('tipogasto__codigo','tipogasto__nombre').order_by('tipogasto__codigo').annotate(ejecutado=Sum('ejecutado'))
        rubros = glue(rubros_inicial, rubros_final, periodo, 'tipogasto__codigo', actualizado=rubros_actualizado)

        source_inicial = GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL,).\
            values('gasto__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_final = GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL,).\
            values('gasto__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

        # grafico de ejecutado y asignado a nivel nacional (distintas clases)
        sql_tpl="SELECT clasificacion,\
                (SELECT SUM({quesumar}) FROM core_GastoDetalle JOIN core_Gasto ON core_GastoDetalle.gasto_id=core_Gasto.id JOIN core_TipoGasto ON core_GastoDetalle.tipogasto_id=core_TipoGasto.codigo \
                JOIN lugar_clasificacionmunicano ON core_Gasto.municipio_id=lugar_clasificacionmunicano.municipio_id AND core_Gasto.anio=lugar_clasificacionmunicano.anio \
                WHERE core_Gasto.anio={year} AND core_Gasto.periodo='{periodo}' AND lugar_clasificacionmunicano.clasificacion_id=clase.id ) \
                AS {quesumar} FROM lugar_clasificacionmunic AS clase ORDER BY clasificacion"
        sql = sql_tpl.format(quesumar="asignado", year=year, periodo=PERIODO_INICIAL,)
        cursor = connection.cursor()
        cursor.execute(sql)
        inicial = dictfetchall(cursor)
        sql = sql_tpl.format(quesumar="ejecutado", year=year, periodo=PERIODO_FINAL,)
        cursor = connection.cursor()
        cursor.execute(sql)
        final = dictfetchall(cursor)
        sql = sql_tpl.format(quesumar="ejecutado", year=year, periodo=PERIODO_ACTUALIZADO,)
        cursor = connection.cursor()
        cursor.execute(sql)
        actualizado = dictfetchall(cursor)
        porclase = glue(inicial, final, PERIODO_INICIAL, 'clasificacion', actualizado=actualizado)
        for d in porclase:
            if d['actualizado']:
                d['nivel'] = d['ejecutado'] / d['actualizado'] * 100
            else:
                d['nivel'] = 0

        # grafico de ejecutado y asignado a nivel nacional (distintas clases) porcentage
        sql_tpl="SELECT clasificacion,\
                (SELECT SUM({quesumar}) FROM core_GastoDetalle JOIN core_Gasto ON core_GastoDetalle.gasto_id=core_Gasto.id JOIN core_TipoGasto ON core_GastoDetalle.tipogasto_id=core_TipoGasto.codigo \
                JOIN lugar_clasificacionmunicano ON core_Gasto.municipio_id=lugar_clasificacionmunicano.municipio_id AND core_Gasto.anio=lugar_clasificacionmunicano.anio \
                WHERE core_Gasto.anio={year} AND core_Gasto.periodo='{periodo}' AND lugar_clasificacionmunicano.clasificacion_id=clase.id) /\
                (SELECT SUM(poblacion) FROM lugar_Poblacion \
                JOIN lugar_clasificacionmunicano ON lugar_Poblacion.municipio_id = lugar_clasificacionmunicano.municipio_id \
                JOIN lugar_clasificacionmunic ON lugar_clasificacionmunicano.clasificacion_id=lugar_clasificacionmunic.id \
                WHERE lugar_Poblacion.anio={year} AND lugar_clasificacionmunic.clasificacion=clase.clasificacion)\
                AS {quesumar} FROM lugar_clasificacionmunic AS clase ORDER BY clasificacion"
        sql = sql_tpl.format(quesumar="asignado", year=year, periodo=PERIODO_INICIAL,)
        cursor = connection.cursor()
        cursor.execute(sql)
        inicial = dictfetchall(cursor)
        sql = sql_tpl.format(quesumar="ejecutado", year=year, periodo=PERIODO_FINAL,)
        cursor = connection.cursor()
        cursor.execute(sql)
        final = dictfetchall(cursor)
        sql = sql_tpl.format(quesumar="ejecutado", year=year, periodo=PERIODO_ACTUALIZADO,)
        cursor = connection.cursor()
        cursor.execute(sql)
        actualizado = dictfetchall(cursor)
        porclasep = glue(inicial, final, PERIODO_INICIAL, 'clasificacion', actualizado=actualizado)

        # obtiene datos para grafico comparativo de tipo de gastos
        tipo_inicial= list(GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_INICIAL).values('subsubtipogasto__origen__nombre').order_by('subsubtipogasto__origen__nombre').annotate(asignado=Sum('asignado')))
        tipo_final = list(GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_FINAL).values('subsubtipogasto__origen__nombre').order_by('subsubtipogasto__origen__nombre').annotate(ejecutado=Sum('ejecutado')))
        tipo = glue(tipo_inicial, tipo_final, periodo, 'subsubtipogasto__origen__nombre')

        # obtiene datos para OGM comparativo de un año específico
        inicial = list(GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_INICIAL).values('gasto__periodo').annotate(monto=Sum('asignado')).order_by('gasto__periodo'))
        actualizado = list(GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_ACTUALIZADO).values('gasto__periodo').annotate(monto=Sum('ejecutado')).order_by('gasto__periodo'))
        final = list(GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_FINAL).values('gasto__periodo').annotate(monto=Sum('ejecutado')).order_by('gasto__periodo'))
        comparativo2 = list(chain(inicial, final, ))
        comparativo3 = list(chain(inicial, final, actualizado))
        for d in comparativo3:
            d.update((k, PERIODO_VERBOSE[v]) for k, v in d.iteritems() if k == "gasto__periodo")
        
        # obtiene datos para OGM comparativo de todos los años
        anios_inicial = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL).values('gasto__anio', 'gasto__periodo').order_by('gasto__anio', 'gasto__periodo').annotate(asignado=Sum('asignado')))
        anios_final = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL).values('gasto__anio', 'gasto__periodo').order_by('gasto__anio', 'gasto__periodo').annotate(ejecutado=Sum('ejecutado')))
        comparativo_anios = glue(anios_inicial, anios_final, periodo, 'gasto__anio')

        # obtiene valores para este año de las listas
        try:
            asignado = (item for item in source_inicial if item["gasto__anio"] == int(year)).next()['asignado']
        except StopIteration:
            asignado = 0
        try:
            ejecutado = (item for item in source_final if item["gasto__anio"] == int(year)).next()['ejecutado']
        except StopIteration:
            ejecutado = 0
        source = glue(source_inicial, source_final, periodo, 'gasto__anio')


    #
    # chartit!
    #
    if municipio:
        ogm_comparativo_anios = RawDataPool(
            series=
                [{'options': {'source': comparativo_anios },
                'terms':  ['gasto__anio','gasto__periodo','municipio_inicial','municipio_final','clase_inicial','clase_final'],
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
                    'gasto__anio': ['municipio_inicial', 'clase_inicial', 'municipio_final', 'clase_final'],
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
    else: # no municipio
        ogm_comparativo_anios = RawDataPool(
            series=
                [{'options': {'source': comparativo_anios },
                'terms':  ['gasto__anio','gasto__periodo','asignado','ejecutado',],
                }],
            )
        ogm_comparativo2 = RawDataPool(
            series=
                [{'options': {'source': comparativo2 },
                'terms':  ['gasto__periodo', 'monto'],
                }],
                )
        ogm_comparativo3 = RawDataPool(
            series=
                [{'options': {'source': comparativo3 },
                'terms':  ['gasto__periodo', 'monto'],
                }],
                )
        ogm_comparativo2_column = Chart(
                datasource = ogm_comparativo2,
                series_options =
                [{'options':{
                    'type': 'column',
                    'stacking': False},
                    'terms':{
                    'gasto__periodo': ['monto',]
                    },
                    }],
                chart_options =
                {'title': { 'text': 'gastos %s' % (year)}},
                )
        ogm_comparativo3_column = Chart(
                datasource = ogm_comparativo3,
                series_options =
                [{'options':{
                    'type': 'column',
                    'stacking': False},
                    'terms':{
                    'gasto__periodo': ['monto', ]
                    },
                    }],
                chart_options =
                {'title': { 'text': 'gastos %s' % (year)}},
                )
        ogm_comparativo_anios_column = Chart(
                datasource = ogm_comparativo_anios,
                series_options =
                [{'options':{
                    'type': 'column',
                    'stacking': False},
                    'terms':{
                    'gasto__anio': ['ejecutado', 'asignado'],
                    },
                    }],
                chart_options =
                {'title': { 'text': 'gastos %s' % (municipio,)}},
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
                        'categories': 'gasto__anio',
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
                        'categories': 'gasto__anio',
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

    asignado_pie = Chart(
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
                'plotOptions': { 'pie': { 'dataLabels': { 'enabled': True, 'format': '{point.percentage:.1f} %' }, 'showInLegend': True, 'depth': 35}},
                'tooltip': { 'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>' },
            }
    )

    ejecutado_pie = Chart(
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
                  'title': {'text': 'Destino del gasto'},
                  'options3d': { 'enabled': 'true',  'alpha': '45', 'beta': '0' },
                  'plotOptions': { 'pie': { 'dataLabels': { 'enabled': True, 'format': '{point.percentage:.1f} %' }, 'showInLegend': True, 'depth': 35}},
                  'tooltip': { 'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>' },
              })

    # tabla: get total and percent
    total = {}
    total['ejecutado'] = sum(item['ejecutado'] for item in sources)
    total['asignado'] = sum(item['asignado'] for item in sources)
    for row in sources:
        row['ejecutado_percent'] = round(row['ejecutado'] / total['ejecutado'] * 100, 0) if total['ejecutado'] > 0 else 0
        row['asignado_percent'] = round(row['asignado'] / total['asignado'] * 100, 0) if total['asignado'] > 0 else 0

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
            value = source_cuadro.filter(gasto__anio=ayear, gasto__periodo=periodo, subsubtipogasto__origen__nombre=label).aggregate(total=Sum(quesumar))['total']
            porano_table[label][ayear] = value if value else ''
        if municipio and year:
            periodo = PERIODO_FINAL
            quesumar = 'ejecutado'
            value = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=periodo, subsubtipogasto__origen__nombre=label, \
                    gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, gasto__municipio__clase__anio=year).\
                    aggregate(total=Sum(quesumar))['total']
            if value:
                value = value / mi_clase_count
            porano_table[label]['extra'] = value if value else '...'

    if portada:
        charts =  (ejecutado_pie, )
    elif municipio:
        charts =  (ejecutado_pie, ogm_comparativo_anios_column, ogm_comparativo2_column, ogm_comparativo3_column, ogm_tipo_column, asignado_barra, barra, )
    else:
        charts =  (ejecutado_pie, ogm_comparativo_anios_column, ogm_comparativo2_column, ogm_comparativo3_column, ogm_tipo_column, asignado_barra, barra, )

    return {'charts': charts, \
            'mi_clase': mi_clase, 'municipio': municipio_row, 'anio': year, 'porano': porano_table, 'totales': sources, \
            'ejecutado': ejecutado, 'asignado': asignado, 'year_list': year_list, 'municipio_list': municipio_list, \
            'anuales': anual2, 'porclase': porclase, 'porclasep': porclasep, 'rubros': rubros, 'rubrosp': rubrosp, 'otros': otros}
