# -*- coding: utf-8 -*-
##############################################################################
#
# Gastos de personal charts /core/gpersonal
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

from core.models import Anio, IngresoDetalle, Ingreso, GastoDetalle, Gasto, Inversion, Proyecto, Municipio, TipoGasto, InversionFuente, InversionFuenteDetalle, CatInversion, ClasificacionMunicAno
from core.models import PERIODO_INICIAL, PERIODO_ACTUALIZADO, PERIODO_FINAL, PERIODO_VERBOSE
from core.tools import getYears, dictfetchall, glue
from core.charts.misc import getVar


def gpersonal_chart(request):

    municipio_list = Municipio.objects.all()
    municipio = getVar('municipio', request)
    year_list = getYears(Gasto)
    year = getVar('year', request)
    if not year:
        year = year_list[-2]

    periodo = Anio.objects.get(anio=year).periodo
    quesumar = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'

    from collections import OrderedDict #FIXME move up
    if municipio:
        porclase = None
        porclasep = None
        municipio_row = Municipio.objects.get(slug=municipio)
        municipio_id = municipio_row.id
        municipio_nombre = municipio_row.nombre
        source_inicial = GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL, \
            tipogasto=TipoGasto.PERSONAL, gasto__municipio__slug=municipio).\
            values('gasto__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_final = GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL, \
            tipogasto=TipoGasto.PERSONAL, gasto__municipio__slug=municipio).\
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
                tipogasto=TipoGasto.PERSONAL, gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion).\
                values('gasto__municipio__nombre', 'gasto__municipio__slug').order_by('gasto__municipio__nombre').annotate(asignado=Sum('asignado'))
        municipios_actualizado = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_ACTUALIZADO, gasto__municipio__clase__anio=year, \
                tipogasto=TipoGasto.PERSONAL, gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion).\
                values('gasto__municipio__nombre', 'gasto__municipio__slug').order_by('gasto__municipio__nombre').annotate(asignado=Sum('asignado'))
        municipios_final = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_FINAL, gasto__municipio__clase__anio=year, \
                tipogasto=TipoGasto.PERSONAL, gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion).\
                values('gasto__municipio__nombre', 'gasto__municipio__slug').order_by('gasto__municipio__nombre').annotate(ejecutado=Sum('ejecutado'))
        otros = glue(municipios_inicial, municipios_final, 'gasto__municipio__nombre', actualizado=municipios_actualizado)
        # inserta porcentages de total de gastos
        for row in otros:
            total = {}
            total['asignado'] = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_INICIAL,\
                gasto__municipio__nombre=row['gasto__municipio__nombre']).aggregate(asignado=Sum('asignado'))['asignado']
            total['ejecutado'] = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_FINAL,\
                gasto__municipio__nombre=row['gasto__municipio__nombre']).aggregate(ejecutado=Sum('ejecutado'))['ejecutado']
            row['ejecutado_percent'] = round(row['ejecutado'] / total['ejecutado'] * 100, 1) if total['ejecutado'] > 0 else 0
            row['asignado_percent'] = round(row['asignado'] / total['asignado'] * 100, 1) if total['asignado'] > 0 else 0
        otros = sorted(otros, key=itemgetter('ejecutado_percent'), reverse=True)

        # obtiene datos de gastos en ditintos rubros de corriente (clasificacion 0)
        rubros_inicial = GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL, \
                tipogasto=TipoGasto.PERSONAL,).\
                values('subtipogasto__codigo','subtipogasto__nombre').order_by('subtipogasto__codigo').annotate(asignado=Sum('asignado'))
        rubros_actualizado = GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio, gasto__periodo=PERIODO_ACTUALIZADO, \
                tipogasto=TipoGasto.PERSONAL,).\
                values('subtipogasto__codigo','subtipogasto__nombre').order_by('subtipogasto__codigo').annotate(asignado=Sum('asignado'))
        rubros_final= GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio, gasto__periodo=PERIODO_FINAL, \
                tipogasto=TipoGasto.PERSONAL,).\
                values('subtipogasto__codigo','subtipogasto__nombre').order_by('subtipogasto__codigo').annotate(ejecutado=Sum('ejecutado'))
        rubros = glue(rubros_inicial, rubros_final, 'subtipogasto__codigo', actualizado=rubros_actualizado)

        # obtiene datos comparativo de todos los años
        inicial = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL, tipogasto=TipoGasto.PERSONAL,).values('gasto__anio', 'gasto__periodo').annotate(asignado=Sum('asignado')))
        final = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_FINAL, tipogasto=TipoGasto.PERSONAL,).values('gasto__anio', 'gasto__periodo').annotate(ejecutado=Sum('ejecutado')))
        anual2 = glue(inicial=inicial, final=final, key='gasto__anio')
        final_clase_sql = "SELECT core_gasto.anio AS gasto__anio,'F' AS gasto__periodo,SUM(ejecutado) AS clase_final FROM core_gastodetalle JOIN core_gasto ON core_gastodetalle.gasto_id=core_gasto.id \
        JOIN lugar_clasificacionmunicano ON core_gasto.municipio_id=lugar_clasificacionmunicano.municipio_id AND \
        core_gasto.anio=lugar_clasificacionmunicano.anio JOIN core_tipogasto ON core_gastodetalle.tipogasto_id=core_tipogasto.codigo \
        WHERE core_gasto.periodo=%s AND core_tipogasto.clasificacion=%s \
        AND lugar_clasificacionmunicano.clasificacion_id=(SELECT clasificacion_id FROM lugar_clasificacionmunicano WHERE municipio_id=%s AND lugar_clasificacionmunicano.anio=core_gasto.anio) \
        GROUP BY core_gasto.anio"
        cursor = connection.cursor()
        cursor.execute(final_clase_sql, [PERIODO_FINAL, TipoGasto.CORRIENTE, municipio_id])
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

        # obtiene datos para grafico comparativo de tipo de gastos
        tipo_inicial= list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__anio=year, gasto__periodo=PERIODO_INICIAL, tipogasto=TipoGasto.PERSONAL).values('subtipogasto__nombre').annotate(asignado=Sum('asignado')))
        tipo_final = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__anio=year, gasto__periodo=PERIODO_FINAL, tipogasto=TipoGasto.PERSONAL).values('subtipogasto__nombre').annotate(ejecutado=Sum('ejecutado')))
        tipo = glue(tipo_inicial, tipo_final, 'subtipogasto__nombre')

        # obtiene datos comparativo de todos los años
        #inicial = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL, tipogasto=TipoGasto.PERSONAL,).values('gasto__anio', 'gasto__periodo').annotate(municipio_inicial=Sum('asignado')))
        final = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_FINAL, tipogasto=TipoGasto.PERSONAL,).values('gasto__anio', 'gasto__periodo').annotate(municipio_final=Sum('ejecutado')))
        # obtiene datos para municipio de la misma clase
        #inicial_clase = GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL, tipogasto=TipoGasto.PERSONAL, \
        #        gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, gasto__municipio__clase__anio=year).\
        #        values('gasto__anio','gasto__periodo').order_by('gasto__periodo').annotate(clase_inicial=Sum('asignado'))
        final_clase_sql = "SELECT core_gasto.anio AS gasto__anio,'F' AS gasto__periodo,SUM(ejecutado) AS clase_final FROM core_gastodetalle JOIN core_gasto ON core_gastodetalle.gasto_id=core_gasto.id \
        JOIN lugar_clasificacionmunicano ON core_gasto.municipio_id=lugar_clasificacionmunicano.municipio_id AND \
        core_gasto.anio=lugar_clasificacionmunicano.anio JOIN core_tipogasto ON core_gastodetalle.tipogasto_id=core_tipogasto.codigo \
        WHERE core_gasto.periodo=%s AND core_tipogasto.codigo=%s \
        AND lugar_clasificacionmunicano.clasificacion_id=(SELECT clasificacion_id FROM lugar_clasificacionmunicano WHERE municipio_id=%s AND lugar_clasificacionmunicano.anio=core_gasto.anio) \
        GROUP BY core_gasto.anio"
        cursor = connection.cursor()
        cursor.execute(final_clase_sql, [PERIODO_FINAL, TipoGasto.PERSONAL, municipio_id])
        final_clase = dictfetchall(cursor)
        # inserta datos para municipio de la misma clase
        #for row in inicial:
        #    for row2 in inicial_clase:
        #        if row2['gasto__anio'] == row['gasto__anio']:
        #            row['clase_inicial'] = row2['clase_inicial'] / mi_clase_anios_count[row['gasto__anio']]
        for row in final:
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
        #for row in inicial:
        #    found = False
        #    for row2 in final:
        #        if row2['gasto__anio'] == row['gasto__anio']:
        #            found = True
        #            row['clase_final'] = row2['clase_final'] / mi_clase_anios_count[row['gasto__anio']]
        #            row['municipio_final'] = row2['municipio_final']
        #        if not found:
        #            row['clase_final'] = 0
        #            row['municipio_final'] = 0
        #comparativo_anios = inicial
        comparativo_anios = final

        # comparativo con promedio de clasificacion para un año específico
        inicial = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL, \
            gasto__anio=year, tipogasto=TipoGasto.PERSONAL, gasto__municipio__slug=municipio).\
            values('gasto__periodo').annotate(municipio=Sum('asignado')))
        actualizado = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_ACTUALIZADO, \
            gasto__anio=year, tipogasto=TipoGasto.PERSONAL, gasto__municipio__slug=municipio).\
            values('gasto__periodo').annotate(municipio=Sum('asignado')))
        final = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL, \
            gasto__anio=year, tipogasto=TipoGasto.PERSONAL, gasto__municipio__slug=municipio).\
            values('gasto__periodo').annotate(municipio=Sum('ejecutado')))

        # obtiene datos para municipio de la misma clase
        inicial_clase = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_INICIAL,\
                tipogasto=TipoGasto.PERSONAL, \
                gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, gasto__municipio__clase__anio=year).\
                values('gasto__periodo').order_by('gasto__periodo').annotate(clase=Sum('asignado'))
        actualizado_clase = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_ACTUALIZADO,\
                tipogasto=TipoGasto.PERSONAL, \
                gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, gasto__municipio__clase__anio=year).\
                values('gasto__periodo').order_by('gasto__periodo').annotate(clase=Sum('asignado'))
        final_clase = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_FINAL,\
                tipogasto=TipoGasto.PERSONAL, \
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

        gasto_promedio = GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL, \
            tipogasto=TipoGasto.PERSONAL, \
            gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, gasto__municipio__clase__anio=year).\
            values('gasto__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        try:
            for record in source_inicial:
                record['ejecutado'] = source_final.filter(gasto__anio=record['gasto__anio'])[0]['ejecutado']
                record['promedio'] = gasto_promedio.filter(gasto__anio=record['gasto__anio'])[0]['asignado']
        except IndexError:
            record['promedio'] = 0 #FIXME: really?
            pass

        source = source_inicial
        #source = OrderedDict(sorted(source.items(), key=lambda t: t[0]))
            
        # FIXME. igual que abajo (sin municipio) de donde tomar los datos?
        source_barra = GastoDetalle.objects.filter( gasto__periodo=PERIODO_INICIAL, \
            tipogasto=TipoGasto.PERSONAL, gasto__municipio__slug=municipio).\
            values('gasto__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_barra_final = source_barra # FIXME este es un work-around

        # chart: porcentage gastos de personal
        source_pgf_asignado =  GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL, tipogasto=TipoGasto.PERSONAL).aggregate(asignado=Sum('asignado'))
        source_pgf_asignado['nombre'] = 'Personal'
        otros_asignado = GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL).exclude(tipogasto=TipoGasto.PERSONAL).aggregate(asignado=Sum('asignado'))
        otros_asignado['nombre'] = 'Otros'
        source_pgf = [source_pgf_asignado, otros_asignado]
    else:
        #
        # no municipio
        #
        otros = None
        mi_clase = None
        municipio = ''

        # obtiene datos comparativo de todos los años
        inicial = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL, tipogasto=TipoGasto.PERSONAL,).values('gasto__anio', 'gasto__periodo').annotate(asignado=Sum('asignado')))
        final = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL, tipogasto=TipoGasto.PERSONAL,).values('gasto__anio', 'gasto__periodo').annotate(ejecutado=Sum('ejecutado')))
        anual2 = glue(inicial=inicial, final=final, key='gasto__anio')

        source_inicial = GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL, \
            tipogasto=TipoGasto.PERSONAL).\
            values('gasto__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_final = GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL, \
            tipogasto=TipoGasto.PERSONAL).\
            values('gasto__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        for record in source_inicial:
            try:
                record['ejecutado'] = source_final.filter(gasto__anio=record['gasto__anio'])[0]['ejecutado']
            except IndexError:
                record['ejecutado'] = 0
        source = source_inicial

        # obtiene valores para este año de las listas
        try:
            asignado = (item for item in source_inicial if item["gasto__anio"] == int(year)).next()['asignado']
        except StopIteration:
            asignado = 0
        try:
            ejecutado = (item for item in source_final if item["gasto__anio"] == int(year)).next()['ejecutado']
        except StopIteration:
            ejecutado = 0
        source = glue(source_inicial, source_final, 'gasto__anio')

        # grafico de ejecutado y asignado a nivel nacional (distintas clases)
        sql_tpl="SELECT clasificacion,\
                (SELECT SUM({quesumar}) FROM core_GastoDetalle JOIN core_Gasto ON core_GastoDetalle.gasto_id=core_Gasto.id JOIN core_TipoGasto ON core_GastoDetalle.tipogasto_id=core_TipoGasto.codigo \
                JOIN lugar_clasificacionmunicano ON core_Gasto.municipio_id=lugar_clasificacionmunicano.municipio_id AND core_Gasto.anio=lugar_clasificacionmunicano.anio \
                WHERE core_Gasto.anio={year} AND core_Gasto.periodo='{periodo}' AND core_tipogasto.codigo='{tipogasto}' AND lugar_clasificacionmunicano.clasificacion_id=clase.id ) \
                AS {quesumar} FROM lugar_clasificacionmunic AS clase ORDER BY clasificacion"
        sql = sql_tpl.format(quesumar="asignado", year=year, periodo=PERIODO_INICIAL, tipogasto=TipoGasto.PERSONAL, )
        cursor = connection.cursor()
        cursor.execute(sql)
        inicial = dictfetchall(cursor)
        sql = sql_tpl.format(quesumar="ejecutado", year=year, periodo=PERIODO_FINAL, tipogasto=TipoGasto.PERSONAL, )
        cursor = connection.cursor()
        cursor.execute(sql)
        final = dictfetchall(cursor)
        sql = sql_tpl.format(quesumar="asignado", year=year, periodo=PERIODO_ACTUALIZADO, tipogasto=TipoGasto.PERSONAL, )
        cursor = connection.cursor()
        cursor.execute(sql)
        actualizado = dictfetchall(cursor)
        porclase = glue(inicial, final, 'clasificacion', actualizado=actualizado)
        for d in porclase:
            if d['actualizado'] and d['ejecutado']:
                d['nivel'] = d['ejecutado'] / d['actualizado'] * 100
            else:
                d['nivel'] = 0

        # grafico de ejecutado y asignado a nivel nacional (distintas clases) porcentage
        sql_tpl="SELECT clasificacion,\
                (SELECT SUM({quesumar}) FROM core_GastoDetalle JOIN core_Gasto ON core_GastoDetalle.gasto_id=core_Gasto.id JOIN core_TipoGasto ON core_GastoDetalle.tipogasto_id=core_TipoGasto.codigo \
                JOIN lugar_clasificacionmunicano ON core_Gasto.municipio_id=lugar_clasificacionmunicano.municipio_id AND core_Gasto.anio=lugar_clasificacionmunicano.anio \
                WHERE core_Gasto.anio={year} AND core_Gasto.periodo='{periodo}' AND core_tipogasto.codigo='{tipogasto}' AND lugar_clasificacionmunicano.clasificacion_id=clase.id) /\
                (SELECT SUM({quesumar}) FROM core_GastoDetalle JOIN  core_Gasto ON core_GastoDetalle.gasto_id=core_Gasto.id JOIN core_TipoGasto ON core_GastoDetalle.tipogasto_id=core_TipoGasto.codigo \
                JOIN lugar_clasificacionmunicano ON core_Gasto.municipio_id=lugar_clasificacionmunicano.municipio_id AND core_Gasto.anio=lugar_clasificacionmunicano.anio \
                WHERE core_Gasto.anio={year} AND core_Gasto.periodo='{periodo}' AND lugar_clasificacionmunicano.clasificacion_id=clase.id HAVING SUM({quesumar})>0) * 100 \
                AS {quesumar} FROM lugar_clasificacionmunic AS clase ORDER BY clasificacion"
        sql = sql_tpl.format(quesumar="asignado", year=year, periodo=PERIODO_INICIAL, tipogasto=TipoGasto.PERSONAL)
        cursor = connection.cursor()
        cursor.execute(sql)
        inicial = dictfetchall(cursor)
        sql = sql_tpl.format(quesumar="ejecutado", year=year, periodo=PERIODO_FINAL, tipogasto=TipoGasto.PERSONAL)
        cursor = connection.cursor()
        cursor.execute(sql)
        final = dictfetchall(cursor)
        sql = sql_tpl.format(quesumar="asignado", year=year, periodo=PERIODO_ACTUALIZADO, tipogasto=TipoGasto.PERSONAL)
        cursor = connection.cursor()
        cursor.execute(sql)
        actualizado = dictfetchall(cursor)
        porclasep = glue(inicial, final, 'clasificacion', actualizado=actualizado)

        # obtiene datos de gastos en ditintos rubros de corriente (clasificacion 0)
        rubros_inicial = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_INICIAL, tipogasto=TipoGasto.PERSONAL,).\
                values('subtipogasto__codigo','subtipogasto__nombre').order_by('subtipogasto__codigo').annotate(asignado=Sum('asignado'))
        rubros_actualizado = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_ACTUALIZADO, tipogasto=TipoGasto.PERSONAL,).\
                values('subtipogasto__codigo','subtipogasto__nombre').order_by('subtipogasto__codigo').annotate(asignado=Sum('asignado'))
        rubros_final= GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_FINAL, tipogasto=TipoGasto.PERSONAL,).\
                values('subtipogasto__codigo','subtipogasto__nombre').order_by('subtipogasto__codigo').annotate(ejecutado=Sum('ejecutado'))
        rubros = glue(rubros_inicial, rubros_final, 'subtipogasto__codigo', actualizado=rubros_actualizado)

        # obtiene datos para grafico comparativo de tipo de gastos
        tipo_inicial= list(GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_INICIAL).values('subtipogasto__nombre').annotate(asignado=Sum('asignado')))
        tipo_final = list(GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_FINAL).values('subtipogasto__nombre').annotate(ejecutado=Sum('ejecutado')))
        tipo = glue(tipo_inicial, tipo_final, 'subtipogasto__nombre')

        # FIXME. en el grafico de periodos...  de donde tomar los datos?
        source_barra_inicial = GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL, \
            tipogasto=TipoGasto.PERSONAL).\
            values('gasto__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_barra_final = GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL, \
            tipogasto=TipoGasto.PERSONAL).\
            values('gasto__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

        # chart: porcentage gastos de personal
        source_pgf_asignado =  GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_INICIAL, tipogasto=TipoGasto.PERSONAL).aggregate(asignado=Sum('asignado'))
        source_pgf_asignado['nombre'] = 'Personal'
        otros_asignado = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_INICIAL).exclude(tipogasto=TipoGasto.PERSONAL).aggregate(asignado=Sum('asignado'))
        otros_asignado['nombre'] = 'Otros'
        source_pgf = [source_pgf_asignado, otros_asignado]

        # comparativo con promedio de clasificacion para un año específico
        inicial = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL, \
            gasto__anio=year, tipogasto__clasificacion=TipoGasto.CORRIENTE, ).\
            values('gasto__periodo').annotate(municipio=Sum('asignado')))
        actualizado = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_ACTUALIZADO, \
            gasto__anio=year, tipogasto__clasificacion=TipoGasto.CORRIENTE, ).\
            values('gasto__periodo').annotate(municipio=Sum('ejecutado')))
        final = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL, \
            gasto__anio=year, tipogasto__clasificacion=TipoGasto.CORRIENTE, ).\
            values('gasto__periodo').annotate(municipio=Sum('ejecutado')))
        comparativo3 = list(chain(inicial, actualizado, final))
        comparativo2 = list(chain(inicial, final, ))
        for d in comparativo3:
            d.update((k, PERIODO_VERBOSE[v]) for k, v in d.iteritems() if k == "gasto__periodo")

        # obtiene datos comparativo de todos los años
        final = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL, tipogasto__clasificacion=TipoGasto.CORRIENTE,).values('gasto__anio', 'gasto__periodo').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')))
        comparativo_anios = final


    #
    # chartit!
    #
    if municipio:
        gf_comparativo_anios = RawDataPool(
            series=
                [{'options': {'source': comparativo_anios },
                'names':  ['Anios',u'Periodo',u'Mi Municipio',u'Categoria %s' % (mi_clase.clasificacion,)],
                'terms':  ['gasto__anio','gasto__periodo','municipio_final','clase_final'],
                }],
            )
        gf_comparativo_anios_column = Chart(
                datasource = gf_comparativo_anios,
                series_options =
                [{'options':{
                    'type': 'column',
                    'stacking': False},
                    'terms':{
                    'gasto__anio': ['municipio_final', 'clase_final'],
                    },
                    }],
                chart_options =
                {'title': { 'text': ' '}},
                )
        gf_comparativo3 = RawDataPool(
            series=
                [{'options': {'source': comparativo3 },
                'names':  [u'Gastos',u'Mi municipio',u'Categoría %s' % (mi_clase.clasificacion,)],
                'terms':  ['gasto__periodo','municipio','clase'],
                }],
                #sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
                )
        gf_comparativo3_column = Chart(
                datasource = gf_comparativo3,
                series_options =
                [{'options':{
                    'type': 'column',
                    'stacking': False},
                    'terms':{
                    'gasto__periodo': ['municipio', 'clase']
                    },
                    }],
                chart_options =
                {'title': { 'text': ' '}},
                )
        gf_comparativo2 = RawDataPool(
            series=
                [{'options': {'source': comparativo2 },
                'names':  [u'Gastos',u'Mi municipio',u'Categoría %s' % (mi_clase.clasificacion,)],
                'terms':  ['gasto__periodo','municipio','clase'],
                }],
                #sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
                )
        gf_comparativo2_column = Chart(
                datasource = gf_comparativo2,
                series_options =
                [{'options':{
                    'type': 'column',
                    'stacking': False},
                    'terms':{
                    'gasto__periodo': ['municipio', 'clase']
                    },
                    }],
                chart_options =
                {'title': { 'text': ' '}},
                )
    else: # chartit no municipio
        gf_nivelejecucion = RawDataPool(
            series=
                [{'options': {'source': porclase },
                'terms':  ['clasificacion','ejecutado','actualizado','nivel'],
                }],
            )
        gf_nivelejecucion_bar = Chart(
                datasource = gf_nivelejecucion,
                series_options =
                [{'options':{
                    'type': 'bar',
                    'stacking': False},
                    'terms':{
                    'clasificacion': ['nivel' ],
                    },
                    }],
                chart_options = {
                    'title': { 'text': u' '},
                    'tooltip': { 'pointFormat': '{series.name}: <b>{point.y:.1f}%</b>' },
                    }
                )
        gf_comparativo_anios = RawDataPool(
            series=
                [{'options': {'source': comparativo_anios },
                'names': [u'Año',u'Periodo',u'Ejecutado','P. Inicial'],
                'terms':  ['gasto__anio','gasto__periodo','ejecutado','asignado'],
                }],
            )
        gf_comparativo_anios_column = Chart(
                datasource = gf_comparativo_anios,
                series_options =
                [{'options':{
                    'type': 'column',
                    'stacking': False},
                    'terms':{
                    'gasto__anio': ['ejecutado', 'asignado' ],
                    },
                    }],
                chart_options =
                {'title': { 'text': ' '}},
                )
        gf_comparativo3 = RawDataPool(
            series=
                [{'options': {'source': comparativo3 },
                'terms':  ['gasto__periodo','municipio',],
                }],
                #sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
                )
        gf_comparativo3_column = Chart(
                datasource = gf_comparativo3,
                series_options =
                [{'options':{
                    'type': 'column',
                    'stacking': False},
                    'terms':{
                    'gasto__periodo': ['municipio',]
                    },
                    }],
                chart_options =
                {'title': { 'text': ' '}},
                )
        gf_comparativo2 = RawDataPool(
            series=
                [{'options': {'source': comparativo2 },
                'terms':  ['gasto__periodo','municipio',],
                }],
                #sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
                )
        gf_comparativo2_column = Chart(
                datasource = gf_comparativo2,
                series_options =
                [{'options':{
                    'type': 'column',
                    'stacking': False},
                    'terms':{
                    'gasto__periodo': ['municipio', ]
                    },
                    }],
                chart_options = {
                    'title': { 'text': ' '},
                    'tooltip': { 'pointFormat': '{series.name}: <b>{point.y:.1f}%</b>' },
                }
                )

    personal_tipo = RawDataPool(
        series=
            [{'options': {'source': tipo },
            'terms':  ['subtipogasto__nombre','ejecutado','asignado'],
            }],
        )
    personal_tipo_column = Chart(
            datasource = personal_tipo,
            series_options =
            [{'options':{
                'type': 'column',
                'stacking': False},
                'terms':{
                'subtipogasto__nombre': ['ejecutado', 'asignado'],
                },
                }],
            chart_options =
            {
                'title': { 'text': ' '},
                'data': { 'table': 'datatable'},
            },
    )
    data_pgf = RawDataPool(
           series = [{
              'options': {'source': source_pgf },
              'terms': [ 'nombre', 'asignado', ]
            }]
    )
    pie = Chart(
            datasource = data_pgf,
            series_options = [{
                'options': {'type': 'pie',},
                'terms': {'nombre': ['asignado']}
            }],
            chart_options = {
                'title': {'text': ' '},
                'options3d': { 'enabled': 'true',  'alpha': '45', 'beta': '0' },
                'plotOptions': { 'pie': { 'dataLabels': { 'enabled': True, 'format': '{point.percentage:.1f} %' }, 'showInLegend': True, 'depth': 35}},
                'tooltip': { 'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>' },
            },
    )
    data_barra = DataPool(
           series = [{
              'options': {'source': source_barra_final },
              'terms': [ 'gasto__anio', 'ejecutado', 'asignado', ]
            }]
    )

    barra = Chart(
            datasource = data_barra,
            series_options =
              [{'options':{
                  'type': 'column',},
                'terms':{
                  'gasto__anio': [
                    'asignado',
                    'ejecutado']
                  }}],
            chart_options = {
                'title': {'text': ' '},
                'options3d': { 'enabled': 'true',  'alpha': 0, 'beta': 0, 'depth': 50 },
                },
            )
    if municipio:
        dataterms = ['gasto__anio', 'asignado', 'ejecutado', 'promedio']
        terms = ['asignado', 'ejecutado', 'promedio',]
    else:
        municipio = ''
        municipio_row = ''
        dataterms = ['gasto__anio', 'asignado', 'ejecutado']
        terms = ['asignado', 'ejecutado']

    data = RawDataPool(series = [{'options': {'source': source }, 'terms': dataterms}])
    gfbar = Chart(
            datasource = data,
            series_options = [{'options': {'type': 'column'}, 'terms': {'gasto__anio': terms }}],
            chart_options = {
                'title': {'text': u' '},
                'options3d': { 'enabled': 'true',  'alpha': 0, 'beta': 0, 'depth': 50 },
                },
            #x_sortf_mapf_mts = (None, lambda i:  i.strftime('%Y'), False)
            )

    portada = False #FIXME: convert to view
    if portada:
        charts =  (pie, )
    elif municipio:
        charts =  (gfbar, barra, pie, gf_comparativo2_column, gf_comparativo3_column, gf_comparativo_anios_column)
    else:
        charts =  (gfbar, barra, pie, gf_comparativo2_column, gf_comparativo3_column, gf_comparativo_anios_column, gf_nivelejecucion_bar)
        
    #Descarga en Excel
    reporte = request.POST.get("reporte","") 
    if "excel" in request.POST.keys() and reporte:        
        from core.utils import obtener_excel_response
        
        data = {'charts': charts, 'municipio': municipio_row, 'municipio_list': municipio_list, 'year_list': year_list,\
            'otros': otros, 'rubros': rubros, 'anuales': anual2, 'ejecutado': ejecutado, 'asignado': asignado, 'porclase': porclase, \
            'porclasep': porclasep, 'mi_clase': mi_clase, 'year': year}
                 
        return obtener_excel_response(reporte=reporte, data=data)
            
    return render_to_response('personal.html',{'charts': charts, 'municipio': municipio_row, 'municipio_list': municipio_list, 'year_list': year_list,\
            'otros': otros, 'rubros': rubros, 'anuales': anual2, 'ejecutado': ejecutado, 'asignado': asignado, 'porclase': porclase, \
            'porclasep': porclasep, 'mi_clase': mi_clase, 'year': year},
            context_instance=RequestContext(request))
