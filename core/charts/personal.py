# -*- coding: utf-8 -*-
##############################################################################
#
# Gastos de personal charts /core/gpersonal
#
##############################################################################
import json

from itertools import chain
from datetime import datetime, time
from operator import itemgetter

from django.db import connection
from django.db.models import Q, Sum, Max, Min, Avg, Count
from django.shortcuts import render_to_response, render
from django.template import RequestContext

from chartit import DataPool, Chart, PivotDataPool, PivotChart, RawDataPool

from core.models import Anio, IngresoDetalle, Ingreso, GastoDetalle, Gasto, Inversion, Proyecto, Municipio, TipoGasto, InversionFuente, InversionFuenteDetalle, CatInversion
from core.models import PERIODO_INICIAL, PERIODO_ACTUALIZADO, PERIODO_FINAL, PERIODO_VERBOSE
from core.tools import (getYears, getPeriods, dictfetchall,
                        glue, superglue, xnumber,
                        graphChart)
from core.charts.misc import getVar
from lugar.models import ClasificacionMunicAno

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

colors_array = [
    '#37a2da',
    '#314454',
    '#ce8266',
    '#9ee6b7',
    '#ffdb5c',
    '#ff9f7e',
    '#fb7292',
    '#e062ae',
    '#e690d2',
    '#e7bcf3',
    '#9d95f5',
    '#67a0a8',
    '#96bfff',
]

chart_options = getattr(
    pma_settings,
    'CHART_OPTIONS',
    {}
)


def gpersonal_chart(request):

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

    # obtiene codigo de tipo gasto de 'mapping' fallback a valor por defecto definido en models
    TipoGasto.PERSONAL = year_data.mapping.get('gpersonal', TipoGasto.PERSONAL)
    PERSONALES = [amap['gpersonal'] for amap in Anio.objects.all().
                  values_list('mapping', flat=True).distinct()]

    quesumar = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'
    datacol = 'inicial_asignado' if periodo == PERIODO_INICIAL else 'ejecutado'

    if municipio:
        porclase = None
        porclasep = None
        municipio_row = Municipio.objects.get(slug=municipio)
        municipio_id = municipio_row.id
        municipio_nombre = municipio_row.nombre
        source_inicial = GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL,
                                                     tipogasto=TipoGasto.PERSONAL, gasto__municipio__slug=municipio).\
            values('gasto__anio').order_by('gasto__anio').annotate(
                ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_final = GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL,
                                                   tipogasto=TipoGasto.PERSONAL, gasto__municipio__slug=municipio).\
            values('gasto__anio').order_by('gasto__anio').annotate(
                ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_periodo = GastoDetalle.objects.filter(gasto__periodo=periodo,
                                                     tipogasto=TipoGasto.PERSONAL, gasto__municipio__slug=municipio).\
            values('gasto__anio').order_by('gasto__anio').annotate(
                ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

        # obtiene valores para este año de las listas
        try:
            asignado = (item for item in source_inicial if item["gasto__anio"] == int(
                year)).next()['asignado']
        except StopIteration:
            asignado = 0
        try:
            ejecutado = (item for item in source_periodo if item["gasto__anio"] == int(year)).next()[
                'ejecutado']
        except StopIteration:
            ejecutado = 0

        # obtiene clase y contador (otros en misma clase) para este año
        mi_clase = ClasificacionMunicAno.objects.get(municipio__slug=municipio, anio=year)
        mi_clase_count = ClasificacionMunicAno.objects.filter(
            clasificacion__clasificacion=mi_clase.clasificacion, anio=year).count()
        # obtiene clase y contador (otros en misma clase) para todos los años
        mi_clase_anios = list(ClasificacionMunicAno.objects.filter(
            municipio__slug=municipio).values('anio', 'clasificacion__clasificacion').annotate())
        mi_clase_anios_count = {}
        for aclase in mi_clase_anios:
            mi_clase_anios_count[aclase['anio']] = ClasificacionMunicAno.objects.filter(
                clasificacion__clasificacion=aclase['clasificacion__clasificacion'], anio=aclase['anio']).count()

        # obtiene datos de municipios de la misma clase
        municipios_inicial = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_INICIAL, gasto__municipio__clase__anio=year,
                                                         tipogasto=TipoGasto.PERSONAL, gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion).\
            values('gasto__municipio__nombre', 'gasto__municipio__slug').order_by('gasto__municipio__nombre').annotate(
                inicial_asignado=Sum('asignado'), inicial_ejecutado=Sum('ejecutado'))
        municipios_actualizado = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_ACTUALIZADO, gasto__municipio__clase__anio=year,
                                                             tipogasto=TipoGasto.PERSONAL, gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion).\
            values('gasto__municipio__nombre', 'gasto__municipio__slug').order_by('gasto__municipio__nombre').annotate(
                actualizado_asignado=Sum('asignado'), actualizado_ejecutado=Sum('ejecutado'))
        municipios_final = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_FINAL, gasto__municipio__clase__anio=year,
                                                       tipogasto=TipoGasto.PERSONAL, gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion).\
            values('gasto__municipio__nombre', 'gasto__municipio__slug').order_by(
                'gasto__municipio__nombre').annotate(final_asignado=Sum('asignado'), final_ejecutado=Sum('ejecutado'))
        municipios_periodo = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=periodo, gasto__municipio__clase__anio=year,
                                                         tipogasto=TipoGasto.PERSONAL, gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion).\
            values('gasto__municipio__nombre', 'gasto__municipio__slug').order_by(
                'gasto__municipio__nombre').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        #otros = glue(municipios_inicial, municipios_final, 'gasto__municipio__nombre', actualizado=municipios_actualizado)
        otros = superglue(data=(municipios_inicial, municipios_final,
                                municipios_actualizado, municipios_periodo), key='gasto__municipio__nombre')
        # inserta porcentages de total de gastos
        for row in otros:
            total = {}
            total['asignado'] = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_INICIAL,
                                                            gasto__municipio__nombre=row['gasto__municipio__nombre']).aggregate(asignado=Sum('asignado'))['asignado']
            total['ejecutado'] = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=periodo,
                                                             gasto__municipio__nombre=row['gasto__municipio__nombre']).aggregate(ejecutado=Sum('ejecutado'))['ejecutado']
            row['ejecutado_percent'] = round(
                row['ejecutado'] / total['ejecutado'] * 100, 2) if total['ejecutado'] > 0 else 0
            row['asignado_percent'] = round(
                row['asignado'] / total['asignado'] * 100, 2) if total['asignado'] > 0 else 0
        sort_key = "{}_percent".format(quesumar)
        otros = sorted(otros, key=itemgetter(sort_key), reverse=False)

        # obtiene datos de gastos en ditintos rubros de corriente (clasificacion 0)
        rubros_inicial = GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL,
                                                     tipogasto=TipoGasto.PERSONAL,).\
            values('subtipogasto__codigo', 'subtipogasto__nombre', 'subtipogasto__shortname').order_by(
                'subtipogasto__codigo').annotate(inicial_asignado=Sum('asignado'))
        rubros_actualizado = GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio, gasto__periodo=PERIODO_ACTUALIZADO,
                                                         tipogasto=TipoGasto.PERSONAL,).\
            values('subtipogasto__codigo', 'subtipogasto__nombre', 'subtipogasto__shortname').order_by(
                'subtipogasto__codigo').annotate(actualizado_asignado=Sum('asignado'), actualizado_ejecutado=Sum('ejecutado'))
        rubros_final = GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio, gasto__periodo=PERIODO_FINAL,
                                                   tipogasto=TipoGasto.PERSONAL,).\
            values('subtipogasto__codigo', 'subtipogasto__nombre', 'subtipogasto__shortname').order_by(
                'subtipogasto__codigo').annotate(final_asignado=Sum('asignado'), final_ejecutado=Sum('ejecutado'))
        rubros_periodo = GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio, gasto__periodo=periodo,
                                                     tipogasto=TipoGasto.PERSONAL,).\
            values('subtipogasto__codigo', 'subtipogasto__nombre', 'subtipogasto__shortname').order_by(
                'subtipogasto__codigo').annotate(ejecutado=Sum('ejecutado'))
        #rubros = glue(rubros_inicial, rubros_final, 'subtipogasto__codigo', actualizado=rubros_actualizado)
        rubros = superglue(data=(rubros_inicial, rubros_final, rubros_actualizado,
                                 rubros_periodo), key='subtipogasto__codigo')

        # obtiene datos comparativo de todos los años
        inicial = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL,
                                                   tipogasto__in=PERSONALES).values('gasto__anio', 'gasto__periodo').annotate(asignado=Sum('asignado')).order_by())
        final = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_FINAL,
                                                 tipogasto__in=PERSONALES).values('gasto__anio', 'gasto__periodo').annotate(ejecutado=Sum('ejecutado')).order_by())
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
        tipo_inicial = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__anio=year, gasto__periodo=PERIODO_INICIAL,
                                                        tipogasto=TipoGasto.PERSONAL).values('subtipogasto__nombre').annotate(asignado=Sum('asignado')))
        tipo_final = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__anio=year, gasto__periodo=PERIODO_FINAL,
                                                      tipogasto=TipoGasto.PERSONAL).values('subtipogasto__nombre').annotate(ejecutado=Sum('ejecutado')))
        tipo = glue(tipo_inicial, tipo_final, 'subtipogasto__nombre')

        # obtiene datos comparativo de todos los años
        #inicial = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL, tipogasto=TipoGasto.PERSONAL,).values('gasto__anio', 'gasto__periodo').annotate(municipio_inicial=Sum('asignado')))
        final = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_FINAL,
                                                 tipogasto=TipoGasto.PERSONAL,).values('gasto__anio', 'gasto__periodo').annotate(municipio_final=Sum('ejecutado')))
        # obtiene datos para municipio de la misma clase
        # inicial_clase = GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL, tipogasto=TipoGasto.PERSONAL, \
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
                        row['clase_final'] = row2['clase_final'] / \
                            mi_clase_anios_count[row['gasto__anio']]
                    except KeyError:
                        row['clase_final'] = 0
            if not found:
                row['clase_final'] = 0
        # for row in inicial:
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
        inicial = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL,
                                                   gasto__anio=year, tipogasto=TipoGasto.PERSONAL, gasto__municipio__slug=municipio).
                       values('gasto__periodo').annotate(municipio=Sum('asignado')))
        actualizado = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_ACTUALIZADO,
                                                       gasto__anio=year, tipogasto=TipoGasto.PERSONAL, gasto__municipio__slug=municipio).
                           values('gasto__periodo').annotate(municipio=Sum('asignado')))
        final = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL,
                                                 gasto__anio=year, tipogasto=TipoGasto.PERSONAL, gasto__municipio__slug=municipio).
                     values('gasto__periodo').annotate(municipio=Sum('ejecutado')))

        # obtiene datos para municipio de la misma clase
        inicial_clase = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_INICIAL,
                                                    tipogasto=TipoGasto.PERSONAL,
                                                    gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, gasto__municipio__clase__anio=year).\
            values('gasto__periodo').order_by('gasto__periodo').annotate(clase=Sum('asignado'))
        actualizado_clase = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_ACTUALIZADO,
                                                        tipogasto=TipoGasto.PERSONAL,
                                                        gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, gasto__municipio__clase__anio=year).\
            values('gasto__periodo').order_by('gasto__periodo').annotate(clase=Sum('asignado'))
        final_clase = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_FINAL,
                                                  tipogasto=TipoGasto.PERSONAL,
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

        gasto_promedio = GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL,
                                                     tipogasto=TipoGasto.PERSONAL,
                                                     gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, gasto__municipio__clase__anio=year).\
            values('gasto__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        for record in source_inicial:
            try:
                record['ejecutado'] = source_final.filter(
                    gasto__anio=record['gasto__anio'])[0]['ejecutado']
                record['promedio'] = gasto_promedio.filter(
                    gasto__anio=record['gasto__anio'])[0]['asignado']
            except IndexError:
                record['promedio'] = 0  # FIXME: really?
                pass

        source = source_inicial
        #source = OrderedDict(sorted(source.items(), key=lambda t: t[0]))

        # FIXME. igual que abajo (sin municipio) de donde tomar los datos?
        source_barra = GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL,
                                                   tipogasto=TipoGasto.PERSONAL, gasto__municipio__slug=municipio).\
            values('gasto__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_barra_final = source_barra  # FIXME este es un work-around

        # chart: porcentage gastos de personal
        source_pgf_asignado = GastoDetalle.objects.filter(
            gasto__municipio__slug=municipio, gasto__anio=year, gasto__periodo=periodo, tipogasto=TipoGasto.PERSONAL).aggregate(asignado=Sum(quesumar))
        source_pgf_asignado['nombre'] = 'Personal'
        otros_asignado = GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__anio=year, gasto__periodo=periodo).exclude(
            tipogasto=TipoGasto.PERSONAL).aggregate(asignado=Sum(quesumar))
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
        inicial = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL,
                                                   tipogasto__in=PERSONALES).values('gasto__anio', 'gasto__periodo').
                       annotate(asignado=Sum('asignado')).order_by())
        final = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL,
                                                 tipogasto__in=PERSONALES).values('gasto__anio', 'gasto__periodo').
                     annotate(ejecutado=Sum('ejecutado')).order_by())
        anual2 = glue(inicial=inicial, final=final, key='gasto__anio')

        source_inicial = GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL,
                                                     tipogasto=TipoGasto.PERSONAL).\
            values('gasto__anio').order_by('gasto__anio').annotate(
                ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_final = GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL,
                                                   tipogasto=TipoGasto.PERSONAL).\
            values('gasto__anio').order_by('gasto__anio').annotate(
                ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_periodo = GastoDetalle.objects.filter(gasto__periodo=periodo,
                                                     tipogasto=TipoGasto.PERSONAL).\
            values('gasto__anio').order_by('gasto__anio').annotate(
                ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        for record in source_inicial:
            try:
                record['ejecutado'] = source_final.filter(
                    gasto__anio=record['gasto__anio'])[0]['ejecutado']
            except IndexError:
                record['ejecutado'] = 0
        source = source_inicial

        # obtiene valores para este año de las listas
        try:
            asignado = (item for item in source_inicial if item["gasto__anio"] == int(
                year)).next()['asignado']
        except StopIteration:
            asignado = 0
        try:
            ejecutado = (item for item in source_periodo if item["gasto__anio"] == int(year)).next()[
                'ejecutado']
        except StopIteration:
            ejecutado = 0
        source = glue(source_inicial, source_final, 'gasto__anio')

        # grafico de ejecutado y asignado a nivel nacional (distintas clases)
        sql_tpl = "SELECT clasificacion,\
                (SELECT SUM(asignado) AS {asignado} FROM core_GastoDetalle JOIN core_Gasto ON core_GastoDetalle.gasto_id=core_Gasto.id JOIN core_TipoGasto ON core_GastoDetalle.tipogasto_id=core_TipoGasto.codigo \
                JOIN lugar_clasificacionmunicano ON core_Gasto.municipio_id=lugar_clasificacionmunicano.municipio_id AND core_Gasto.anio=lugar_clasificacionmunicano.anio \
                WHERE core_Gasto.anio={year} AND core_Gasto.periodo='{periodo}' AND core_tipogasto.codigo='{tipogasto}' AND lugar_clasificacionmunicano.clasificacion_id=clase.id ), \
                (SELECT SUM(ejecutado) AS {ejecutado} FROM core_GastoDetalle JOIN core_Gasto ON core_GastoDetalle.gasto_id=core_Gasto.id JOIN core_TipoGasto ON core_GastoDetalle.tipogasto_id=core_TipoGasto.codigo \
                JOIN lugar_clasificacionmunicano ON core_Gasto.municipio_id=lugar_clasificacionmunicano.municipio_id AND core_Gasto.anio=lugar_clasificacionmunicano.anio \
                WHERE core_Gasto.anio={year} AND core_Gasto.periodo='{periodo}' AND core_tipogasto.codigo='{tipogasto}' AND lugar_clasificacionmunicano.clasificacion_id=clase.id ) \
                FROM lugar_clasificacionmunic AS clase ORDER BY clasificacion"
        sql = sql_tpl.format(asignado="inicial_asignado", ejecutado='inicial_ejecutado',
                             year=year, periodo=PERIODO_INICIAL, tipogasto=TipoGasto.PERSONAL, )
        cursor = connection.cursor()
        cursor.execute(sql)
        inicial = dictfetchall(cursor)
        sql = sql_tpl.format(asignado="final_asignado", ejecutado="final_ejecutado",
                             year=year, periodo=PERIODO_FINAL, tipogasto=TipoGasto.PERSONAL, )
        cursor = connection.cursor()
        cursor.execute(sql)
        final = dictfetchall(cursor)
        sql = sql_tpl.format(asignado="asignado", ejecutado="ejecutado",
                             year=year, periodo=periodo, tipogasto=TipoGasto.PERSONAL, )
        cursor = connection.cursor()
        cursor.execute(sql)
        porclase_periodo = dictfetchall(cursor)
        sql = sql_tpl.format(asignado="actualizado_asignado", ejecutado="actualizado_ejecutado",
                             year=year, periodo=PERIODO_ACTUALIZADO, tipogasto=TipoGasto.PERSONAL, )
        cursor = connection.cursor()
        cursor.execute(sql)
        actualizado = dictfetchall(cursor)
        porclase = superglue(data=(inicial, final, actualizado,
                                   porclase_periodo), key='clasificacion')
        for d in porclase:
            if d['asignado'] and d['ejecutado']:
                d['nivel'] = d['ejecutado'] / d['asignado'] * 100
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
        sql = sql_tpl.format(quesumar="asignado", year=year,
                             periodo=PERIODO_INICIAL, tipogasto=TipoGasto.PERSONAL)
        cursor = connection.cursor()
        cursor.execute(sql)
        inicial = dictfetchall(cursor)
        sql = sql_tpl.format(quesumar="ejecutado", year=year,
                             periodo=periodo, tipogasto=TipoGasto.PERSONAL)
        cursor = connection.cursor()
        cursor.execute(sql)
        final = dictfetchall(cursor)
        sql = sql_tpl.format(quesumar="asignado", year=year,
                             periodo=PERIODO_ACTUALIZADO, tipogasto=TipoGasto.PERSONAL)
        cursor = connection.cursor()
        cursor.execute(sql)
        actualizado = dictfetchall(cursor)
        porclasep = glue(inicial, final, 'clasificacion', actualizado=actualizado)

        # obtiene datos de gastos en ditintos rubros de corriente (clasificacion 0)
        rubros_inicial = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_INICIAL, tipogasto=TipoGasto.PERSONAL,).\
            values('subtipogasto__codigo', 'subtipogasto__nombre', 'subtipogasto__shortname').order_by(
                'subtipogasto__codigo').annotate(inicial_asignado=Sum('asignado'))
        rubros_actualizado = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_ACTUALIZADO, tipogasto=TipoGasto.PERSONAL,).\
            values('subtipogasto__codigo', 'subtipogasto__nombre', 'subtipogasto__shortname').order_by(
                'subtipogasto__codigo').annotate(actualizado_asignado=Sum('asignado'), actualizado_ejecutado=Sum('ejecutado'))
        rubros_final = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_FINAL, tipogasto=TipoGasto.PERSONAL,).\
            values('subtipogasto__codigo', 'subtipogasto__nombre', 'subtipogasto__shortname').order_by(
                'subtipogasto__codigo').annotate(final_asignado=Sum('asignado'), final_ejecutado=Sum('ejecutado'))
        rubros_periodo = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=periodo, tipogasto=TipoGasto.PERSONAL,).\
            values('subtipogasto__codigo', 'subtipogasto__nombre', 'subtipogasto__shortname').order_by(
                'subtipogasto__codigo').annotate(ejecutado=Sum('ejecutado'))
        #rubros = glue(rubros_inicial, rubros_final, 'subtipogasto__codigo', actualizado=rubros_actualizado)
        rubros = superglue(data=(rubros_inicial, rubros_final, rubros_actualizado,
                                 rubros_periodo), key='subtipogasto__codigo')

        # obtiene datos para grafico comparativo de tipo de gastos
        tipo_inicial = list(GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_INICIAL).values(
            'subtipogasto__nombre').annotate(asignado=Sum('asignado')))
        tipo_final = list(GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_FINAL).values(
            'subtipogasto__nombre').annotate(ejecutado=Sum('ejecutado')))
        tipo = glue(tipo_inicial, tipo_final, 'subtipogasto__nombre')

        # FIXME. en el grafico de periodos...  de donde tomar los datos?
        source_barra_inicial = GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL,
                                                           tipogasto=TipoGasto.PERSONAL).\
            values('gasto__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_barra_final = GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL,
                                                         tipogasto=TipoGasto.PERSONAL).\
            values('gasto__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

        # chart: porcentage gastos de personal
        source_pgf_asignado = GastoDetalle.objects.filter(
            gasto__anio=year, gasto__periodo=periodo, tipogasto=TipoGasto.PERSONAL).aggregate(asignado=Sum('asignado'))
        source_pgf_asignado['nombre'] = 'Personal'
        otros_asignado = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=periodo).exclude(
            tipogasto=TipoGasto.PERSONAL).aggregate(asignado=Sum('asignado'))
        otros_asignado['nombre'] = 'Otros'
        source_pgf = [source_pgf_asignado, otros_asignado]

        # comparativo con promedio de clasificacion para un año específico
        inicial = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL,
                                                   gasto__anio=year, tipogasto__clasificacion=TipoGasto.CORRIENTE, ).
                       values('gasto__periodo').annotate(municipio=Sum('asignado')))
        actualizado = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_ACTUALIZADO,
                                                       gasto__anio=year, tipogasto__clasificacion=TipoGasto.CORRIENTE, ).
                           values('gasto__periodo').annotate(municipio=Sum('ejecutado')))
        final = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL,
                                                 gasto__anio=year, tipogasto__clasificacion=TipoGasto.CORRIENTE, ).
                     values('gasto__periodo').annotate(municipio=Sum('ejecutado')))
        comparativo3 = list(chain(inicial, actualizado, final))
        comparativo2 = list(chain(inicial, final, ))
        for d in comparativo3:
            d.update((k, PERIODO_VERBOSE[v]) for k, v in d.iteritems() if k == "gasto__periodo")

        # obtiene datos comparativo de todos los años
        final = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL, tipogasto__clasificacion=TipoGasto.CORRIENTE,).values(
            'gasto__anio', 'gasto__periodo').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')))
        comparativo_anios = final

    #
    # chartit!
    #
    if municipio:
        gf_comparativo_anios = RawDataPool(
            series=[{'options': {'source': comparativo_anios},
                     'names':  ['Anios', u'Periodo', u'Mi Municipio', u'Categoria %s' % (mi_clase.clasificacion,)],
                     'terms':  ['gasto__anio', 'gasto__periodo', 'municipio_final', 'clase_final'],
                     }],
        )
        gf_comparativo_anios_column = Chart(
            datasource=gf_comparativo_anios,
            series_options=[{'options': {
                'type': 'column',
                'stacking': False},
                'terms': {
                'gasto__anio': ['municipio_final', 'clase_final'],
            },
            }],
            chart_options={'title': {'text': ' '}},
        )
        gf_comparativo3 = RawDataPool(
            series=[{'options': {'source': comparativo3},
                     'names':  [u'Gastos', u'Mi municipio', u'Categoría %s' % (mi_clase.clasificacion,)],
                     'terms':  ['gasto__periodo', 'municipio', 'clase'],
                     }],
            #sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
        )
        gf_comparativo3_column = Chart(
            datasource=gf_comparativo3,
            series_options=[{'options': {
                'type': 'column',
                'stacking': False},
                'terms': {
                'gasto__periodo': ['municipio', 'clase']
            },
            }],
            chart_options={'title': {'text': ' '}},
        )
        gf_comparativo2 = RawDataPool(
            series=[{'options': {'source': comparativo2},
                     'names':  [u'Gastos', u'Mi municipio', u'Categoría %s' % (mi_clase.clasificacion,)],
                     'terms':  ['gasto__periodo', 'municipio', 'clase'],
                     }],
            #sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
        )
        gf_comparativo2_column = Chart(
            datasource=gf_comparativo2,
            series_options=[{'options': {
                'type': 'column',
                'stacking': False},
                'terms': {
                'gasto__periodo': ['municipio', 'clase']
            },
            }],
            chart_options={'title': {'text': ' '},
                           'yAxis': {'title': {'text': u'Millones de córdobas'}},
                           'xAxis': {'title': {'text': u'Gastos de personal'}}
                           },
        )
    else:  # chartit no municipio
        gf_nivelejecucion = RawDataPool(
            series=[{'options': {'source': porclase},
                     'terms':  ['clasificacion', 'final_ejecutado', 'final_asignado', 'nivel'],
                     }],
        )
        gf_nivelejecucion_bar = Chart(
            datasource=gf_nivelejecucion,
            series_options=[{'options': {
                'type': 'bar',
                'stacking': False},
                'terms': {
                'clasificacion': ['nivel'],
            },
            }],
            chart_options={
                'title': {'text': u' '},
                'tooltip': {'pointFormat': '{series.name}: <b>{point.y:.2f}%</b>'},
            }
        )
        gf_comparativo_anios = RawDataPool(
            series=[{'options': {'source': comparativo_anios},
                     'names': [u'Año', u'Periodo', u'Ejecutado', 'P. Inicial'],
                     'terms':  ['gasto__anio', 'gasto__periodo', 'ejecutado', 'asignado'],
                     }],
        )
        gf_comparativo_anios_column = Chart(
            datasource=gf_comparativo_anios,
            series_options=[{'options': {
                'type': 'column',
                'stacking': False},
                'terms': {
                'gasto__anio': ['ejecutado', 'asignado'],
            },
            }],
            chart_options={'title': {'text': ' '}},
        )
        gf_comparativo3 = RawDataPool(
            series=[{'options': {'source': comparativo3},
                     'terms':  ['gasto__periodo', 'municipio', ],
                     }],
            #sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
        )
        gf_comparativo3_column = Chart(
            datasource=gf_comparativo3,
            series_options=[{'options': {
                'type': 'column',
                'stacking': False},
                'terms': {
                'gasto__periodo': ['municipio', ]
            },
            }],
            chart_options={'title': {'text': ' '}},
        )
        gf_comparativo2 = RawDataPool(
            series=[{'options': {'source': comparativo2},
                     'terms':  ['gasto__periodo', 'municipio', ],
                     }],
            #sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
        )
        gf_comparativo2_column = Chart(
            datasource=gf_comparativo2,
            series_options=[{'options': {
                'type': 'column',
                'stacking': False},
                'terms': {
                'gasto__periodo': ['municipio', ]
            },
            }],
            chart_options={
                'title': {'text': ' '},
                'tooltip': {'pointFormat': '{series.name}: <b>{point.y:.2f}%</b>'},
            }
        )

    personal_tipo = RawDataPool(
        series=[{'options': {'source': tipo},
                 'terms':  ['subtipogasto__nombre', 'ejecutado', 'asignado'],
                 }],
    )
    personal_tipo_column = Chart(
        datasource=personal_tipo,
        series_options=[{'options': {
            'type': 'column',
            'stacking': False},
            'terms': {
            'subtipogasto__nombre': ['ejecutado', 'asignado'],
        },
        }],
        chart_options={
            'title': {'text': ' '},
            'data': {'table': 'datatable'},
        },
    )
    data_pgf = RawDataPool(
        series=[{
            'options': {'source': source_pgf},
            'terms': ['nombre', 'asignado']
        }]
    )
    data_rubros = RawDataPool(
        series=[{
            'options': {'source': rubros},
            'terms': ['subtipogasto__nombre', datacol]
        }])
    pie = Chart(
        datasource=data_rubros,
        series_options=[{
            'options': {'type': 'pie'},
            'terms': {'subtipogasto__nombre': [datacol]}
        }],
        chart_options=chart_options)

    bar = Chart(
        datasource=data_rubros,
        series_options=[{
            'options': {
                'type': 'column',
                'colorByPoint': True,
            },
            'terms': {'subtipogasto__nombre': [datacol]}
        }],
        chart_options=chart_options)

    if municipio:
        dataterms = ['gasto__anio', 'asignado', 'ejecutado', 'promedio']
        terms = ['asignado', 'ejecutado', 'promedio', ]
    else:
        municipio = ''
        municipio_row = ''
        dataterms = ['gasto__anio', 'asignado', 'ejecutado']
        terms = ['asignado', 'ejecutado']

    data = RawDataPool(series=[{'options': {'source': source}, 'terms': dataterms}])
    gfbar = Chart(
        datasource=data,
        series_options=[{'options': {'type': 'column'}, 'terms': {'gasto__anio': terms}}],
        chart_options={
            'title': {'text': u' '},
            'options3d': {'enabled': 'true',  'alpha': 0, 'beta': 0, 'depth': 50},
        },
        #x_sortf_mapf_mts = (None, lambda i:  i.strftime('%Y'), False)
    )

    bar_horizontal = None
    if otros:
        parameters = {
            'data': otros,
            'field1': 'gasto__municipio__nombre',
            'field2': '{}_percent'.format(quesumar),
            'typechart': 'bar',
            'title': "Ranking de Municipios Categoría '{}'".
            format(mi_clase.clasificacion),
            'labelX_axis': 'Municipio',
            'labelY_axis': 'Recaudación por habitante en córdobas corrientes',
            'pointFormat': '<span>Porcentaje del gasto total</span>:<b>{point.y}%</b>',
        }
        bar_horizontal = graphChart(parameters)
    elif porclasep:
        parameters = {
            'data': porclasep,
            'field1': 'clasificacion',
            'field2': quesumar,
            'typechart': 'column',
            'title': 'Porcentaje del Gasto Total',
            'labelX_axis': 'Grupos',
            'labelY_axis': 'Porcentaje',
            'pointFormat': '<span>{series.name}</span>:<b>{point.y:.2f}%</b>',
        }
        bar_horizontal = graphChart(parameters)

    portada = False #FIXME: convert to view
    if portada:
        charts = (pie, )
    elif bar_horizontal:
        charts = (pie, bar, bar_horizontal)
    else:
        charts = (pie, bar)

    # Bubble tree data
    bubble_source = personal_bubbletree_data_gasto(municipio, year, portada)

    # Descarga en Excel
    reporte = request.POST.get("reporte", "")
    if "excel" in request.POST.keys() and reporte:
        from core.utils import obtener_excel_response

        data = {'charts': charts,
                'municipio': municipio_row,
                'municipio_list': municipio_list,
                'year_list': year_list,
                'otros': otros, 'rubros': rubros,
                'anuales': anual2,
                'ejecutado': ejecutado,
                'asignado': asignado,
                'porclase': porclase,
                'porclasep': porclasep,
                'mi_clase': mi_clase,
                'year': year}

        return obtener_excel_response(reporte=reporte, data=data)

    template_name = 'expenses.html'
    context = {'charts': charts, 'municipio': municipio_row,
               'municipio_list': municipio_list, 'year_list': year_list,
               'indicator_name': "Gastos de personal",
               'indicator_description': "Mide el porcentaje del gasto total, destinado a sufragar los salarios y pasivos laborales del personal municipal",
               'otros': otros, 'rubros': rubros, 'anuales': anual2, 'ejecutado': ejecutado, 'asignado': asignado,
               'porclase': porclase,
               'bubble_data': bubble_source,
               'periodo_list': periodo_list,
               'porclasep': porclasep, 'mi_clase': mi_clase,
               'year': year, 'mostraren': "porcentaje",
               }
    return render(request, template_name, context)


def personal_bubbletree_data_gasto(municipio=None, year=None, portada=False):
    year_list = getYears(Gasto)
    periodo_list = getPeriods(Gasto)
    periodo = Anio.objects.get(anio=year).periodo
    if not year:
        year = year_list[-1]
    amount_column = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'
    if municipio:
        tipos = GastoDetalle.objects.filter(
            gasto__anio=year,
            gasto__municipio__slug=municipio,
            gasto__periodo=periodo,
            tipogasto=TipoGasto.PERSONAL)\
            .values('subtipogasto', 'subtipogasto__nombre', 'subtipogasto__shortname')\
            .order_by('subtipogasto__codigo')\
            .annotate(amount=Sum(amount_column))
        amount = GastoDetalle.objects.filter(
            gasto__anio=year,
            gasto__municipio__slug=municipio,
            gasto__periodo=periodo,
            tipogasto=TipoGasto.PERSONAL)\
            .aggregate(total=Sum(amount_column))
    else:
        tipos = GastoDetalle.objects.filter(
            gasto__anio=year,
            gasto__periodo=periodo,
            tipogasto=TipoGasto.PERSONAL)\
            .values('subtipogasto', 'subtipogasto__nombre', 'subtipogasto__shortname')\
            .order_by('subtipogasto__codigo')\
            .annotate(amount=Sum(amount_column))
        amount = GastoDetalle.objects.filter(
            gasto__anio=year,
            gasto__periodo=periodo,
            tipogasto=TipoGasto.PERSONAL)\
            .aggregate(total=Sum(amount_column))
    data = {
        'label': "Gasto de Personal",
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
                subtipogasto__codigo=child['subtipogasto'])\
                .values('subsubtipogasto', 'subsubtipogasto__nombre', 'subsubtipogasto__shortname')\
                .order_by('subsubtipogasto__codigo')\
                .annotate(amount=Sum(amount_column))
        else:
            subtipos = GastoDetalle.objects.filter(
                gasto__anio=year,
                gasto__periodo=periodo,
                subtipogasto__codigo=child['subtipogasto'])\
                .values('subsubtipogasto', 'subsubtipogasto__nombre', 'subsubtipogasto__shortname')\
                .order_by('subsubtipogasto__codigo')\
                .annotate(amount=Sum(amount_column))
        if child['subtipogasto__shortname']:
            label = child['subtipogasto__shortname']
        else:
            label = child['subtipogasto__nombre']
        child_data = {
            'taxonomy': "expense",
            'id': idx,
            'name': idx,
            'label': label,
            'amount': round(xnumber(child['amount']) / 1000000,
                            2)
            }
        children.append(child_data)
    data['children'] = children
    return json.dumps(data)
