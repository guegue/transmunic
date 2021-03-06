# -*- coding: utf-8 -*-
##############################################################################
#
# OGM charts /core/ogm
#
##############################################################################

from itertools import chain
from operator import itemgetter
from collections import OrderedDict

from django.db import connection
from django.db.models import Sum

from chartit import DataPool, Chart, PivotDataPool, PivotChart, RawDataPool
from core.models import (Anio, GastoDetalle, Gasto, Municipio,
                         TipoGasto, PERIODO_INICIAL, PERIODO_ACTUALIZADO,
                         PERIODO_FINAL, PERIODO_VERBOSE)
from core.tools import (getYears, getPeriods, dictfetchall, glue, superglue,
                        percentage, xnumber)
from core.graphics import graphChart
from lugar.models import Poblacion, ClasificacionMunicAno

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


# FIXME: Table date does not match with the original site
def ogm_chart(municipio=None, year=None, portada=False):
    municipio_list = Municipio.objects.all()
    year_list = getYears(Gasto)
    periodo_list = getPeriods(Gasto)
    if not year:
        year = year_list[-1]

    # obtiene último periodo del año que se quiere ver
    year_data = Anio.objects.get(anio=year)
    periodo = year_data.periodo
    datacol = 'inicial_asignado' if periodo == PERIODO_INICIAL else 'ejecutado'

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

        source = GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__anio=year).values(
            'subsubtipogasto__origen__nombre').annotate(**{quesumar: Sum(quesumar)}).order_by('subsubtipogasto__origen__nombre')
        tipos_inicial = GastoDetalle.objects.\
            filter(gasto__municipio__slug=municipio, gasto__anio=year, gasto__periodo=PERIODO_INICIAL).\
            values('subsubtipogasto__origen__nombre', 'subsubtipogasto__origen__orden').\
            annotate(asignado=Sum('asignado')).\
            order_by('subsubtipogasto__origen__orden')
        tipos_final = GastoDetalle.objects.\
            filter(gasto__municipio__slug=municipio, gasto__anio=year, gasto__periodo=periodo).\
            values('subsubtipogasto__origen__nombre', 'subsubtipogasto__origen__orden').\
            annotate(ejecutado=Sum('ejecutado')).\
            order_by('subsubtipogasto__origen__orden')

        sources = glue(tipos_inicial, tipos_final, 'subsubtipogasto__origen__nombre')
        source_barra = GastoDetalle.objects.filter(
            gasto__municipio__slug=municipio, gasto__periodo=periodo, gasto__anio__gt=year_list[-3])
        source_pivot = GastoDetalle.objects.filter(
            gasto__periodo=periodo, gasto__municipio__slug=municipio)

        source_inicial = GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL,
                                                     gasto__municipio__slug=municipio).\
            values('gasto__anio').order_by('gasto__anio').annotate(
                ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_final = GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL,
                                                   gasto__municipio__slug=municipio).\
            values('gasto__anio').order_by('gasto__anio').annotate(
                ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_periodo = GastoDetalle.objects.filter(gasto__periodo=periodo,
                                                     gasto__municipio__slug=municipio).\
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

        # obtiene datos de gastos en ditintos rubros de persoal pemanente (codigo 1100000)
        rubrosp_inicial = GastoDetalle.objects. \
            filter(gasto__anio=year,
                   gasto__municipio__slug=municipio,
                   gasto__periodo=PERIODO_INICIAL,
                   subtipogasto=TipoGasto.PERSONAL_PERMANENTE,). \
            values('subsubtipogasto__codigo',
                   'subsubtipogasto__nombre'). \
            order_by('subsubtipogasto__codigo'). \
            annotate(inicial_asignado=Sum('asignado'))
        rubrosp_actualizado = GastoDetalle.objects. \
            filter(gasto__anio=year,
                   gasto__municipio__slug=municipio,
                   gasto__periodo=PERIODO_ACTUALIZADO,
                   subtipogasto=TipoGasto.PERSONAL_PERMANENTE,). \
            values('subsubtipogasto__codigo',
                   'subsubtipogasto__nombre'). \
            order_by('subsubtipogasto__codigo'). \
            annotate(actualizado_asignado=Sum('asignado'),
                     actualizado_ejecutado=Sum('ejecutado'))
        rubrosp_final = GastoDetalle.objects. \
            filter(gasto__anio=year,
                   gasto__municipio__slug=municipio,
                   gasto__periodo=PERIODO_FINAL,
                   subtipogasto=TipoGasto.PERSONAL_PERMANENTE,). \
            values('subsubtipogasto__codigo',
                   'subsubtipogasto__nombre'). \
            order_by('subsubtipogasto__codigo'). \
            annotate(final_asignado=Sum('asignado'),
                     final_ejecutado=Sum('ejecutado'))
        rubrosp_periodo = GastoDetalle.objects. \
            filter(gasto__anio=year,
                   gasto__municipio__slug=municipio,
                   gasto__periodo=periodo,
                   subtipogasto=TipoGasto.PERSONAL_PERMANENTE,). \
            values('subsubtipogasto__codigo',
                   'subsubtipogasto__nombre'). \
            order_by('subsubtipogasto__codigo'). \
            annotate(ejecutado=Sum('ejecutado'))
        rubrosp = superglue(data=(rubrosp_inicial, rubrosp_final,
                                  rubrosp_actualizado, rubrosp_periodo),
                            key='subsubtipogasto__codigo')

        # obtiene datos de gastos en ditintos rubros de corriente (clasificacion 0)
        rubros_inicial = GastoDetalle.objects. \
            filter(gasto__anio=year,
                   gasto__municipio__slug=municipio,
                   gasto__periodo=PERIODO_INICIAL). \
            values('subsubtipogasto__origen__nombre',
                   'subsubtipogasto__origen__shortname',
                   'subsubtipogasto__origen__orden'). \
            order_by('subsubtipogasto__origen__orden'). \
            annotate(inicial_asignado=Sum('asignado'))
        rubros_actualizado = GastoDetalle.objects. \
            filter(gasto__anio=year,
                   gasto__municipio__slug=municipio,
                   gasto__periodo=PERIODO_ACTUALIZADO). \
            values('subsubtipogasto__origen__nombre',
                   'subsubtipogasto__origen__shortname',
                   'subsubtipogasto__origen__orden'). \
            order_by('subsubtipogasto__origen__orden'). \
            annotate(actualizado_asignado=Sum('asignado'),
                     actualizado_ejecutado=Sum('ejecutado'))
        rubros_final = GastoDetalle.objects. \
            filter(gasto__anio=year,
                   gasto__municipio__slug=municipio,
                   gasto__periodo=PERIODO_FINAL). \
            values('subsubtipogasto__origen__nombre',
                   'subsubtipogasto__origen__shortname',
                   'subsubtipogasto__origen__orden'). \
            order_by('subsubtipogasto__origen__orden'). \
            annotate(final_asignado=Sum('asignado'),
                     final_ejecutado=Sum('ejecutado'))
        rubros_periodo = GastoDetalle.objects.\
            filter(gasto__anio=year,
                   gasto__municipio__slug=municipio,
                   gasto__periodo=periodo,).\
            values('subsubtipogasto__origen__nombre',
                   'subsubtipogasto__origen__shortname',
                   'subsubtipogasto__origen__orden'). \
            order_by('subsubtipogasto__origen__orden'). \
            annotate(ejecutado=Sum('ejecutado'))

        rubros = superglue(data=(rubros_inicial,
                                 rubros_final,
                                 rubros_actualizado,
                                 rubros_periodo),
                           key='subsubtipogasto__origen__nombre')

        # obtiene clase y contador (otros en misma clase) para este año
        mi_clase = ClasificacionMunicAno.objects.get(municipio__slug=municipio, anio=year)
        mi_clase_count = ClasificacionMunicAno.objects.filter(
            clasificacion__clasificacion=mi_clase.clasificacion, anio=year).count()
        # obtiene clase y contador (otros en misma clase) para todos los años
        mi_clase_anios = list(ClasificacionMunicAno.objects.filter(municipio__slug=municipio).values(
            'anio', 'clasificacion__clasificacion').annotate().order_by())
        mi_clase_anios_count = {}
        for aclase in mi_clase_anios:
            mi_clase_anios_count[aclase['anio']] = ClasificacionMunicAno.objects.filter(
                clasificacion__clasificacion=aclase['clasificacion__clasificacion'], anio=aclase['anio']).count()

        # obtiene datos de municipios de la misma clase
        municipios_inicial = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_INICIAL, gasto__municipio__clase__anio=year,
                                                         gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion).\
            values('gasto__municipio__nombre', 'gasto__municipio__slug').annotate(
                asignado=Sum('asignado')).order_by()
        municipios_actualizado = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_ACTUALIZADO, gasto__municipio__clase__anio=year,
                                                             gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion).\
            values('gasto__municipio__nombre', 'gasto__municipio__slug').annotate(
                asignado=Sum('asignado')).order_by()
        municipios_final = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=periodo, gasto__municipio__clase__anio=year,
                                                       gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion).\
            values('gasto__municipio__nombre', 'gasto__municipio__slug').annotate(
                ejecutado=Sum('ejecutado')).order_by()
        otros = glue(municipios_inicial, municipios_final,
                     'gasto__municipio__nombre', actualizado=municipios_actualizado)

        # inserta porcentages de total de gastos
        for row in otros:
            #total_poblacion = Poblacion.objects.filter(anio=year, municipio__clasificaciones__clasificacion=mi_clase.clasificacion)\
            #        .aggregate(poblacion=Sum('poblacion'))['poblacion']
            try:
                total_poblacion = Poblacion.objects.get(
                    anio=year, municipio__slug=row['gasto__municipio__slug']).poblacion
            except:
                total_poblacion = 0
            row['poblacion'] = total_poblacion
            row['ejecutado_percent'] = round(
                row['ejecutado'] / total_poblacion, 1) if total_poblacion > 0 else 0
            row['asignado_percent'] = round(
                row['asignado'] / total_poblacion, 1) if total_poblacion > 0 else 0
        sort_key = "{}_percent".format(quesumar)
        otros = sorted(otros, key=itemgetter(sort_key), reverse=True)

        # obtiene datos para grafico comparativo de tipo de gastos
        tipo_inicial = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__anio=year, gasto__periodo=PERIODO_INICIAL).values(
            'subsubtipogasto__origen__nombre').annotate(asignado=Sum('asignado')).order_by())
        tipo_final = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__anio=year, gasto__periodo=PERIODO_FINAL).values(
            'subsubtipogasto__origen__nombre').annotate(ejecutado=Sum('ejecutado')).order_by())
        tipo = glue(tipo_inicial, tipo_final, 'subsubtipogasto__origen__nombre')

        # obtiene datos comparativo de todos los años FIXME: replaces data below?
        inicial = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL).values(
            'gasto__anio', 'gasto__periodo').annotate(asignado=Sum('asignado')).order_by())
        final = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_FINAL).values(
            'gasto__anio', 'gasto__periodo').annotate(ejecutado=Sum('ejecutado')).order_by())
        anual2 = glue(inicial=inicial, final=final, key='gasto__anio')
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
        inicial = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL).values(
            'gasto__anio', 'gasto__periodo').annotate(municipio_inicial=Sum('asignado')).order_by())
        final = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_FINAL).values(
            'gasto__anio', 'gasto__periodo').annotate(municipio_final=Sum('ejecutado')).order_by())
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
                    if not 'clase_final' in row2:
                        row2['clase_final'] = 0
                    row['clase_final'] = row2['clase_final']
                    row['municipio_final'] = row2['municipio_final']
                if not found:
                    row['clase_final'] = 0
                    row['municipio_final'] = 0
        comparativo_anios = inicial
        # FIXME: no longer? comparativo_anios = list(chain(inicial, final, ))

        # obtiene datos para OGM comparativo de un año específico
        inicial = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__anio=year,
                                                   gasto__periodo=PERIODO_INICIAL).values('gasto__periodo').annotate(municipio=Sum('asignado')).order_by())
        actualizado = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__anio=year,
                                                       gasto__periodo=PERIODO_ACTUALIZADO).values('gasto__periodo').annotate(municipio=Sum('ejecutado')).order_by())
        final = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__anio=year,
                                                 gasto__periodo=PERIODO_FINAL).values('gasto__periodo').annotate(municipio=Sum('ejecutado')).order_by())

        # obtiene datos para municipio de la misma clase
        inicial_clase = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_INICIAL,
                                                    gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, gasto__municipio__clase__anio=year).\
            values('gasto__periodo').order_by('gasto__periodo').annotate(clase=Sum('asignado'))
        actualizado_clase = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_ACTUALIZADO,
                                                        gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, gasto__municipio__clase__anio=year).\
            values('gasto__periodo').order_by('gasto__periodo').annotate(clase=Sum('ejecutado'))
        final_clase = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_FINAL,
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
        inicial = list(GastoDetalle.objects.
                       filter(gasto__periodo=PERIODO_INICIAL).
                       values('gasto__anio',
                              'gasto__periodo').
                       annotate(asignado=Sum('asignado')).
                       order_by())
        final = list(GastoDetalle.objects.
                     filter(gasto__periodo=PERIODO_FINAL).
                     values('gasto__anio',
                            'gasto__periodo').
                     annotate(ejecutado=Sum('ejecutado')).
                     order_by())
        anual2 = glue(inicial=inicial,
                      final=final,
                      key='gasto__anio')

        source = GastoDetalle.objects.\
            filter(gasto__anio=year,
                   gasto__periodo=periodo).\
            values('subsubtipogasto__origen__nombre').\
            annotate(**{quesumar: Sum(quesumar)}).\
            order_by('subsubtipogasto__origen__nombre')
        tipos_inicial = GastoDetalle.objects.\
            filter(gasto__anio=year,
                   gasto__periodo=PERIODO_INICIAL).\
            values('subsubtipogasto__origen__nombre',
                   'subsubtipogasto__origen__slug',
                   'subsubtipogasto__origen__orden').\
            annotate(asignado=Sum('asignado')).\
            order_by('subsubtipogasto__origen__orden')
        tipos_final = GastoDetalle.objects.\
            filter(gasto__anio=year, gasto__periodo=periodo).\
            values('subsubtipogasto__origen__nombre',
                   'subsubtipogasto__origen__slug',
                   'subsubtipogasto__origen__orden').\
            annotate(ejecutado=Sum('ejecutado')).\
            order_by('subsubtipogasto__origen__orden')

        sources = glue(tipos_inicial, tipos_final, 'subsubtipogasto__origen__nombre')
        source_pivot = GastoDetalle.objects.filter(gasto__periodo=periodo)

        source_barra = GastoDetalle.objects.filter(gasto__periodo=periodo)
        source_barra2 = GastoDetalle.objects.filter(
            gasto__periodo=periodo, gasto__anio__gt=year_list[-3])

        # obtiene datos de gastos en ditintos rubros
        rubrosp_inicial = GastoDetalle.objects. \
            filter(gasto__anio=year,
                   gasto__periodo=PERIODO_INICIAL,
                   subtipogasto=TipoGasto.PERSONAL_PERMANENTE,).\
            exclude(tipogasto__codigo=TipoGasto.IMPREVISTOS).\
            values('subsubtipogasto__codigo',
                   'subsubtipogasto__nombre'). \
            order_by('subsubtipogasto__codigo'). \
            annotate(inicial_asignado=Sum('asignado'))
        rubrosp_actualizado = GastoDetalle.objects. \
            filter(gasto__anio=year,
                   gasto__periodo=PERIODO_ACTUALIZADO,
                   subtipogasto=TipoGasto.PERSONAL_PERMANENTE,).\
            exclude(tipogasto__codigo=TipoGasto.IMPREVISTOS).\
            values('subsubtipogasto__codigo',
                   'subsubtipogasto__nombre'). \
            order_by('subsubtipogasto__codigo'). \
            annotate(actualizado_asignado=Sum('asignado'),
                     actualizado_ejecutado=Sum('ejecutado'))
        rubrosp_final = GastoDetalle.objects. \
            filter(gasto__anio=year,
                   gasto__periodo=PERIODO_FINAL,
                   subtipogasto=TipoGasto.PERSONAL_PERMANENTE,).\
            exclude(tipogasto__codigo=TipoGasto.IMPREVISTOS).\
            values('subsubtipogasto__codigo',
                   'subsubtipogasto__nombre'). \
            order_by('subsubtipogasto__codigo'). \
            annotate(final_asignado=Sum('asignado'),
                     final_ejecutado=Sum('ejecutado'))
        rubrosp_periodo = GastoDetalle.objects. \
            filter(gasto__anio=year,
                   gasto__periodo=periodo,
                   subtipogasto=TipoGasto.PERSONAL_PERMANENTE,).\
            exclude(tipogasto__codigo=TipoGasto.IMPREVISTOS).\
            values('subsubtipogasto__codigo',
                   'subsubtipogasto__nombre'). \
            order_by('subsubtipogasto__codigo'). \
            annotate(ejecutado=Sum('ejecutado'))

        rubrosp = superglue(data=(rubrosp_inicial, rubrosp_final,
                                  rubrosp_actualizado, rubrosp_periodo),
                            key='subsubtipogasto__codigo')

        # obtiene datos de gastos en ditintos rubros
        rubros_inicial = GastoDetalle.objects. \
            filter(gasto__anio=year,
                   gasto__periodo=PERIODO_INICIAL). \
            exclude(tipogasto__codigo=TipoGasto.IMPREVISTOS).\
            values('subsubtipogasto__origen__nombre',
                   'subsubtipogasto__origen__shortname',
                   'subsubtipogasto__origen__orden'). \
            order_by('subsubtipogasto__origen__orden'). \
            annotate(inicial_asignado=Sum('asignado'))
        rubros_actualizado = GastoDetalle.objects. \
            filter(gasto__anio=year,
                   gasto__periodo=PERIODO_ACTUALIZADO). \
            exclude(tipogasto__codigo=TipoGasto.IMPREVISTOS).\
            values('subsubtipogasto__origen__nombre',
                   'subsubtipogasto__origen__shortname',
                   'subsubtipogasto__origen__orden'). \
            order_by('subsubtipogasto__origen__orden'). \
            annotate(actualizado_asignado=Sum('asignado'),
                     actualizado_ejecutado=Sum('ejecutado'))
        rubros_final = GastoDetalle.objects.\
            filter(gasto__anio=year,
                   gasto__periodo=PERIODO_FINAL). \
            exclude(tipogasto__codigo=TipoGasto.IMPREVISTOS).\
            values('subsubtipogasto__origen__nombre',
                   'subsubtipogasto__origen__shortname',
                   'subsubtipogasto__origen__orden'). \
            order_by('subsubtipogasto__origen__orden'). \
            annotate(final_asignado=Sum('asignado'),
                     final_ejecutado=Sum('ejecutado'))
        rubros_periodo = GastoDetalle.objects. \
            filter(gasto__anio=year,
                   gasto__periodo=periodo). \
            exclude(tipogasto__codigo=TipoGasto.IMPREVISTOS).\
            values('subsubtipogasto__origen__nombre',
                   'subsubtipogasto__origen__shortname',
                   'subsubtipogasto__origen__orden'). \
            order_by('subsubtipogasto__origen__orden'). \
            annotate(ejecutado=Sum('ejecutado'))

        rubros = superglue(data=(rubros_inicial,
                                 rubros_final,
                                 rubros_actualizado,
                                 rubros_periodo),
                           key='subsubtipogasto__origen__nombre')

        source_inicial = GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL,).\
            values('gasto__anio').order_by('gasto__anio').annotate(
                ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_final = GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL,).\
            values('gasto__anio').order_by('gasto__anio').annotate(
                ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_periodo = GastoDetalle.objects.filter(gasto__periodo=periodo,).\
            values('gasto__anio').order_by('gasto__anio').annotate(
                ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

        # grafico de ejecutado y asignado a nivel nacional (distintas clases)
        sql_tpl = "SELECT clasificacion,\
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
        sql = sql_tpl.format(quesumar="asignado", year=year, periodo=PERIODO_ACTUALIZADO,)
        cursor = connection.cursor()
        cursor.execute(sql)
        actualizado = dictfetchall(cursor)
        porclase = glue(inicial, final, 'clasificacion', actualizado=actualizado)
        for d in porclase:
            if d['actualizado'] and d['asignado']:
                # FIXME: wot? 'asignado' ?
                d['nivel'] = d['asignado'] / d['actualizado'] * 100
            else:
                d['nivel'] = 0

        TipoGasto.PERSONAL = year_data.mapping.get('gpersonal', TipoGasto.PERSONAL)

        # grafico de ejecutado y asignado a nivel nacional (distintas clases) porcentage
        sql_tpl = "SELECT clasificacion,\
                ((SELECT SUM({quesumar}) FROM core_gastodetalle as cgd \
                JOIN core_gasto cg ON cgd.gasto_id=cg.id \
                JOIN core_tipogasto ctg ON cgd.tipogasto_id=ctg.codigo \
                JOIN lugar_clasificacionmunicano lcc ON cg.municipio_id=lcc.municipio_id AND cg.anio=lcc.anio \
                WHERE cg.anio={year} AND cg.periodo='{periodo}' \
                AND ctg.codigo='{tipogasto}' \
                AND lcc.clasificacion_id=clase.id) / \
                (select sum(lp.poblacion) \
                from lugar_poblacion as lp \
                where lp.anio={year} \
                and lp.municipio_id in (select lc.municipio_id \
                from lugar_clasificacionmunicano lc \
                where lc.clasificacion_id = clase.id)))\
                AS {quesumar} FROM lugar_clasificacionmunic AS clase ORDER BY clasificacion"
        sql = sql_tpl.format(quesumar="asignado",
                             year=year,
                             periodo=PERIODO_INICIAL,
                             tipogasto=TipoGasto.PERSONAL)
        cursor = connection.cursor()
        cursor.execute(sql)
        inicial = dictfetchall(cursor)
        sql = sql_tpl.format(quesumar="ejecutado",
                             year=year,
                             periodo=periodo,
                             tipogasto=TipoGasto.PERSONAL)
        cursor = connection.cursor()
        cursor.execute(sql)
        final = dictfetchall(cursor)
        sql = sql_tpl.format(quesumar="asignado",
                             year=year,
                             periodo=PERIODO_ACTUALIZADO,
                             tipogasto=TipoGasto.PERSONAL)
        cursor = connection.cursor()
        cursor.execute(sql)
        actualizado = dictfetchall(cursor)
        porclasep = glue(inicial, final,
                         'clasificacion',
                         actualizado=actualizado)

        # obtiene datos para grafico comparativo de tipo de gastos
        tipo_inicial= list(GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_INICIAL).values('subsubtipogasto__origen__nombre').order_by('subsubtipogasto__origen__nombre').annotate(asignado=Sum('asignado')))
        tipo_final = list(GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_FINAL).values('subsubtipogasto__origen__nombre').order_by('subsubtipogasto__origen__nombre').annotate(ejecutado=Sum('ejecutado')))
        tipo = glue(tipo_inicial, tipo_final, 'subsubtipogasto__origen__nombre')

        # obtiene datos para OGM comparativo de un año específico
        inicial = list(GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_INICIAL).values('gasto__periodo').annotate(monto=Sum('asignado')).order_by('gasto__periodo'))
        actualizado = list(GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_ACTUALIZADO).values('gasto__periodo').annotate(monto=Sum('asignado')).order_by('gasto__periodo'))
        final = list(GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_FINAL).values('gasto__periodo').annotate(monto=Sum('ejecutado')).order_by('gasto__periodo'))
        comparativo2 = list(chain(inicial, final, ))
        comparativo3 = list(chain(inicial, final, actualizado))
        for d in comparativo3:
            d.update((k, PERIODO_VERBOSE[v]) for k, v in d.iteritems() if k == "gasto__periodo")

        # obtiene datos para OGM comparativo de todos los años
        anios_inicial = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL).values('gasto__anio', 'gasto__periodo').order_by('gasto__anio', 'gasto__periodo').annotate(asignado=Sum('asignado')))
        anios_final = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL).values('gasto__anio', 'gasto__periodo').order_by('gasto__anio', 'gasto__periodo').annotate(ejecutado=Sum('ejecutado')))
        comparativo_anios = glue(anios_inicial, anios_final, 'gasto__anio')

        # obtiene valores para este año de las listas
        try:
            asignado = (item for item in source_inicial if item["gasto__anio"] == int(year)).next()['asignado']
        except StopIteration:
            asignado = 0
        try:
            ejecutado = (item for item in source_periodo if item["gasto__anio"] == int(year)).next()['ejecutado']
        except StopIteration:
            ejecutado = 0
        # FIXME que es esto: ???
        source_anios = glue(source_inicial, source_final, 'gasto__anio')


    #
    # chartit!
    #
    if municipio:
        ogm_comparativo_anios = RawDataPool(
            series=
                [{'options': {'source': comparativo_anios },
                'names':  [' ','Periodo',u'P.Inicial',u'P.Final',u'Categoria P. Inicial',u'Categoria P.Final'],
                'terms':  ['gasto__anio','gasto__periodo','municipio_inicial','municipio_final','clase_inicial','clase_final'],
                }],
            )
        ogm_comparativo2 = RawDataPool(
            series=
                [{'options': {'source': comparativo2 },
                'names':  ['Eficiencia en la ejecucion',u'Mi Municipio',u'Categoria %s' % (mi_clase.clasificacion,)],
                'terms':  ['gasto__periodo','municipio','clase'],
                }],
                #sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
                )

        """
        ogm_comparativo3 = RawDataPool(
            series=
                [{'options': {'source': comparativo3 },
                'names':  [' ',u'Mi Municipio',u'Categoria %s' % (mi_clase.clasificacion,)],
                'terms':  ['gasto__periodo','municipio','clase'],
                }],
                #sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
                )
        """
        ogm_comparativo_anios_column = Chart(
                datasource = ogm_comparativo_anios,
                series_options =
                [{'options':{
                    'type': 'column',
                    'stacking': False},
                    'names':  [u'Municipio Inicial',u'Categoria Inicial',u'Municipio Final',u'Categoria Final'],
                    'terms':{
                    'gasto__anio': ['municipio_inicial', 'clase_inicial', 'municipio_final', 'clase_final'],
                    },
                    }],
                chart_options =
                {'title': { 'text': ' '}},
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
                {'title': { 'text': ' '},
                 'yAxis': { 'title': {'text': u'Millones de córdobas'} },
                },
                )
        """
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
                {'title': { 'text': ' '}},
                )
        """
    else: # no municipio
        ogm_comparativo_anios = RawDataPool(
            series=
                [{'options': {'source': comparativo_anios },
                'names':  [' ','Totales','Asignado','Ejecutado'],
                'terms':  ['gasto__anio','gasto__periodo','asignado','ejecutado',],
                }],
            )
        ogm_comparativo2 = RawDataPool(
            series=
                [{'options': {'source': comparativo2 },
                'names':  ['Eficiencia en la ejecucion','Totales'],
                'terms':  ['gasto__periodo', 'monto'],
                }],
                )
        ogm_comparativo3 = RawDataPool(
            series=
                [{'options': {'source': comparativo3 },
                'names':  [' ','Gastos Totales'],
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
                {'title': { 'text': ' '},
                 'yAxis': { 'title': {'text': u'Millones de córdobas'} }
                },
                )
        """
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
                {'title': { 'text': ' '}},
                )
        """
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
                {'title': { 'text': ' '}},
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
                quesumar,
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
                    quesumar ]
                  }}],
            chart_options = {
                'title': { 'text': ' '},
                'options3d': { 'enabled': 'true',  'alpha': '45', 'beta': '0' },
                'plotOptions': { 'pie': { 'dataLabels': { 'enabled': True, 'format': '{point.percentage:.2f} %' }, 'showInLegend': True, 'depth': 35}},
                'tooltip': { 'pointFormat': '{series.name}: <b>{point.percentage:.2f}%</b>' },
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
                    quesumar ]
                  }}],
            chart_options =
              {
                  'title': {'text': ' '},
                  'options3d': { 'enabled': 'true',  'alpha': '45', 'beta': '0' },
                  'plotOptions': { 'pie': { 'dataLabels': { 'enabled': True, 'format': '{point.percentage:.2f} %' }, 'showInLegend': True, 'depth': 35}},
                  'tooltip': { 'pointFormat': '{series.name}: <b>{point.percentage:.2f}%</b>' },
              })

    ''  # llenando rubros_pie que contendra la informacion para los graficos de barra
    ''  # y pastel, resumiendo en un mismo campo el nombre o shortname de cada rubro
    rubros_pie = []
    field_name = 'subsubtipogasto__origen__shortname'
    for row in rubros:
        rubros_pie.append({
            'name': row.get(field_name) or
            row.get('subsubtipogasto__origen__nombre'),
            'inicial_asignado': row.get('inicial_asignado', 0) / 1000000,
            'ejecutado': row.get('ejecutado', 0) / 1000000,
        })

    data_gasto = RawDataPool(
        series=[
            {
                'options': {'source': rubros_pie},
                'terms': [
                    'name',
                    datacol
                ]
            }
        ])

    pie = Chart(
        datasource=data_gasto,
        series_options=[
            {
                'options': {'type': 'pie'},
                'terms': {'name': [datacol]}
            }],
        chart_options=chart_options)

    bar = Chart(
        datasource=data_gasto,
        series_options=[
            {
                'options': {
                    'type': 'column',
                    'colorByPoint': True,
                },
                'terms': {'name': [datacol]}
            }],
        chart_options=chart_options)

    bar_horizontal = None

    # bar horizontal
    if otros:
        parameters = {
            'data': otros,
            'field1': 'gasto__municipio__nombre',
            'field2': '{}_percent'.format(quesumar),
            'typechart': 'bar',
            'title': "Ranking de Municipio Categoría '{}'".
            format(mi_clase.clasificacion),
            'labelX_axis': 'Categoria',
            'labelY_axis': 'Gasto por habitante',
            'pointFormat': '<span>Gasto Inicial</span>:<b>{point.y}</b>',
        }
        bar_horizontal = graphChart(parameters)
    elif porclasep:
        parameters = {
            'data': porclasep,
            'field1': 'clasificacion',
            'field2': quesumar,
            'typechart': 'column',
            'title': 'Gasto por habitante',
            'labelX_axis': 'Ranking de Municipio por Categoría',
            'labelY_axis': 'Municipio',
            'pointFormat': '<span>{series.name}</span>:<b> {point.y:.2f}</b>',
        }
        bar_horizontal = graphChart(parameters)

    # tabla: get total and percent
    total = {
        'ejecutado': sum(item['ejecutado'] for item in sources),
        'asignado': sum(item['asignado'] for item in sources)
    }
    for row in sources:
        row['ejecutado_percent'] = percentage(row['ejecutado'], total['ejecutado'])
        row['asignado_percent'] = percentage(row['asignado'], total['asignado'])

    actualizado = sum(xnumber(row.get('actualizado_asignado')) for row in rubros)

    for row in rubros:
        row['ini_asig_porcentaje'] = percentage(row.get('inicial_asignado', 0), asignado)
        row['actualizado_porcentaje'] = percentage(row.get('actualizado_asignado', 0), actualizado)
        row['ejec_porcentaje'] = percentage(row.get('ejecutado', 0), ejecutado)

    # tabla: get gastos por año
    if municipio:
        source_cuadro = GastoDetalle.objects.filter(gasto__municipio__slug=municipio)
    else:
        source_cuadro = GastoDetalle.objects.all()
    porano_table = {}
    ano_table = {}
    ys = source_cuadro. \
        order_by('subsubtipogasto__origen__nombre'). \
        values('subsubtipogasto__origen__nombre',
               'subsubtipogasto__origen__orden'). \
        distinct()
    for y in ys:
        name = y['subsubtipogasto__origen__nombre']
        if name:
            order = y['subsubtipogasto__origen__orden']
            label = name
            porano_table[label] = {}
            porano_table[label]['orden'] = order
            for ayear in year_list:
                periodo = Anio.objects.get(anio=ayear).periodo
                quesumar = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'
                value = source_cuadro.\
                    filter(gasto__anio=ayear, gasto__periodo=periodo,
                           subsubtipogasto__origen__nombre=name).\
                    aggregate(total=Sum(quesumar))['total']
                porano_table[label][ayear] = {}
                porano_table[label][ayear]['raw'] = value if value else ''
                if not ayear in ano_table:
                    ano_table[ayear] = 0
                ano_table[ayear] += value if value else 0

            if municipio and year:
                periodo = PERIODO_FINAL
                quesumar = 'ejecutado'
                value = GastoDetalle.objects.\
                    filter(gasto__anio=year, gasto__periodo=periodo,
                           subsubtipogasto__origen__nombre=name,
                           gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion,
                           gasto__municipio__clase__anio=year).\
                    aggregate(total=Sum(quesumar))['total']
                if value:
                    value = value / mi_clase_count
                porano_table[label]['extra'] = value if value else '...'

    for y in ys:
        name = y['subsubtipogasto__origen__nombre']
        if name:
            label = name
            for ayear in year_list:
                if porano_table[label][ayear]['raw']:
                    porano_table[label][ayear]['percent'] = format(
                        porano_table[label][ayear]['raw'] / ano_table[ayear], '.2%')

    # ordenar rubros de informacion historica
    porano_table = OrderedDict(sorted(porano_table.iteritems(),
                                      key=lambda x: x[1]['orden']))

    if portada:
        charts = (ejecutado_pie,)
    elif bar_horizontal:
        charts = (pie, bar, bar_horizontal)
    else:
        charts = (pie, bar)

    ''  # ordenando destino de los recursos por campo orden
    sources = sorted(sources, key=lambda i: i['subsubtipogasto__origen__orden'])
    ''  # ordenando rubros por el orden de la bd
    rubros = sorted(rubros, key=lambda i: i['subsubtipogasto__origen__orden'])

    return {
        'charts': charts,
        'year_data': year_data,
        'mi_clase': mi_clase,
        'municipio': municipio_row,
        'year': year,
        'porano': porano_table,
        'totales': sources,
        'ejecutado': ejecutado,
        'asignado': asignado,
        'year_list': year_list,
        'municipio_list': municipio_list,
        'anuales': anual2,
        'porclase': porclase,
        'porclasep': porclasep,
        'rubros': rubros,
        'rubrosp': rubrosp,
        'periodo_list': periodo_list,
        'otros': otros}
