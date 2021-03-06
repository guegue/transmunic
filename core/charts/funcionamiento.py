# -*- coding: utf-8 -*-
##############################################################################
#
# Gastos de funcionamiento charts /core/gf
#
##############################################################################
from itertools import chain
from operator import itemgetter

from django.conf import settings
from django.db import connection
from django.db.models import Sum
from django.shortcuts import render

from chartit import Chart, RawDataPool

from core.models import Anio, GastoDetalle, Gasto, Municipio, TipoGasto
from core.models import PERIODO_INICIAL, PERIODO_ACTUALIZADO, PERIODO_FINAL, PERIODO_VERBOSE
from core.tools import (getYears, getPeriods, dictfetchall,
                        glue, superglue, percentage)
from core.history import historial_gastos_corrientes
from core.graphics import graphChart
from core.charts.misc import getVar
from core.charts.aci import aci_bubbletree_data_gasto
from lugar.models import ClasificacionMunicAno

colorscheme = settings.CHARTS_COLORSCHEME
colors_array = settings.COLORS_ARRAY
chart_options = settings.CHART_OPTIONS


def gf_chart(request):
    # XXX: why this is not a view?
    municipio_list = Municipio.objects.all()
    municipio = getVar('municipio', request)
    periodo_list = getPeriods(Gasto)
    year_list = getYears(Gasto)
    year = getVar('year', request)
    if not year:
        year = year_list[-1]

    periodo = Anio.objects.get(anio=year).periodo
    quesumar = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'
    datacol = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'
    asignado_percent = 0
    ejecutado_percent = 0
    total_nacional_asignado = 0
    total_nacional_ejecutado = 0
    municipio_id = None
    filtro_rubros = {
        'gasto__anio': year,
        'subsubtipogasto__clasificacion': TipoGasto.CORRIENTE
    }
    excluir_cuentas_rubros = {}

    from collections import OrderedDict  # FIXME move up
    if municipio:
        porclase = None
        porclasep = None
        municipio_row = Municipio.objects.get(slug=municipio)
        municipio_id = municipio_row.id
        municipio_nombre = municipio_row.nombre
        source_inicial = GastoDetalle.objects. \
            filter(gasto__periodo=PERIODO_INICIAL,
                   subsubtipogasto__clasificacion=TipoGasto.CORRIENTE,
                   gasto__municipio__slug=municipio). \
            order_by('gasto__anio'). \
            values('gasto__anio'). \
            annotate(ejecutado=Sum('ejecutado'),
                     asignado=Sum('asignado'))
        total_asignado_anio = GastoDetalle.objects. \
            filter(gasto__periodo=PERIODO_INICIAL,
                   gasto__municipio__slug=municipio,
                   gasto__anio=year). \
            order_by('gasto__anio'). \
            values('gasto__anio'). \
            annotate(asignado=Sum('asignado'))
        source_final = GastoDetalle.objects. \
            filter(gasto__periodo=periodo,
                   subsubtipogasto__clasificacion=TipoGasto.CORRIENTE,
                   gasto__municipio__slug=municipio). \
            order_by('gasto__anio'). \
            values('gasto__anio'). \
            annotate(ejecutado=Sum('ejecutado'),
                     asignado=Sum('asignado'))
        total_ejecutado_anio = GastoDetalle.objects. \
            filter(gasto__periodo=periodo,
                   gasto__municipio__slug=municipio,
                   gasto__anio=year). \
            order_by('gasto__anio'). \
            values('gasto__anio'). \
            annotate(ejecutado=Sum('ejecutado'))

        # obtiene valores para este año de las listas
        try:
            asignado = (item for item in source_inicial if item["gasto__anio"] == int(
                year)).next()['asignado']
            total_asignado = total_asignado_anio[0]['asignado']
            asignado_percent = percentage(asignado, total_asignado)
        except StopIteration:
            asignado = 0
        try:
            ejecutado = (item for item in source_final if item["gasto__anio"] == int(year)).next()[
                'ejecutado']
            total_ejecutado = total_ejecutado_anio[0]['ejecutado']
            ejecutado_percent = percentage(ejecutado, total_ejecutado)
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
            mi_clase_anios_count[aclase['anio']] = ClasificacionMunicAno.objects. \
                filter(clasificacion__clasificacion=aclase['clasificacion__clasificacion'],
                       anio=aclase['anio']). \
                count()

        filter_municipio = {
            'gasto__anio': year,
            'gasto__municipio__clase__anio': year,
            'subsubtipogasto__clasificacion': TipoGasto.CORRIENTE,
            'gasto__municipio__clasificaciones__clasificacion': mi_clase.clasificacion
        }

        # obtiene datos de municipios de la misma clase
        municipios_inicial = GastoDetalle.objects. \
            filter(**filter_municipio). \
            filter(gasto__periodo=PERIODO_INICIAL). \
            values('gasto__municipio__id',
                   'gasto__municipio__nombre',
                   'gasto__municipio__slug'). \
            annotate(inicial_asignado=Sum('asignado')). \
            order_by()
        municipios_actualizado = GastoDetalle.objects. \
            filter(**filter_municipio). \
            filter(gasto__periodo=PERIODO_ACTUALIZADO).\
            values('gasto__municipio__id',
                   'gasto__municipio__nombre',
                   'gasto__municipio__slug').\
            annotate(actualizado_asignado=Sum('asignado'),
                     actualizado_ejecutado=Sum('ejecutado')). \
            order_by()
        municipios_final = GastoDetalle.objects. \
            filter(**filter_municipio). \
            filter(gasto__periodo=PERIODO_FINAL). \
            values('gasto__municipio__id',
                   'gasto__municipio__nombre',
                   'gasto__municipio__slug'). \
            annotate(final_asignado=Sum('asignado'),
                     final_ejecutado=Sum('ejecutado')). \
            order_by()
        municipios_periodo = GastoDetalle.objects. \
            filter(**filter_municipio). \
            filter(gasto__periodo=periodo). \
            values('gasto__municipio__id',
                   'gasto__municipio__nombre',
                   'gasto__municipio__slug'). \
            annotate(asignado=Sum('asignado'),
                     ejecutado=Sum('ejecutado')). \
            order_by()

        otros = superglue(data=(municipios_inicial,
                                municipios_final,
                                municipios_actualizado,
                                municipios_periodo),
                          key='gasto__municipio__nombre')

        # inserta porcentages de total de gastos
        total = {
            'total_asignado': 0,
            'total_ejecutado': 0,
            'total_asignado_gp': 0,
            'total_ejecutado_gp': 0
        }
        for row in otros:
            filter_municipio = {
                'gasto__anio': year,
                'gasto__municipio__id': row['gasto__municipio__id']
            }
            total['asignado'] = GastoDetalle.objects. \
                filter(**filter_municipio). \
                filter(gasto__periodo=PERIODO_INICIAL). \
                aggregate(asignado=Sum('asignado'))['asignado']
            total['ejecutado'] = GastoDetalle.objects. \
                filter(**filter_municipio). \
                filter(gasto__periodo=periodo). \
                aggregate(ejecutado=Sum('ejecutado'))['ejecutado']
            row['asignado_percent'] = percentage(row['asignado'], total['asignado'])
            row['ejecutado_percent'] = percentage(row['ejecutado'], total['ejecutado'])
            total['total_asignado_gp'] += row['asignado']
            total['total_ejecutado_gp'] += row['ejecutado'] or 0
            total['total_asignado'] += total['asignado']
            total['total_ejecutado'] += total['ejecutado'] or 0

            # Obteniendo la media nacional
            total_nacional_asignado = percentage(
                total['total_asignado_gp'], total['total_asignado'], 2)
            total_nacional_ejecutado = percentage(
                total['total_ejecutado_gp'], total['total_ejecutado'], 2)

        sort_key = "{}_percent".format(quesumar)
        otros = sorted(otros, key=itemgetter(sort_key), reverse=True)

        # indicando filtro por municipio
        filtro_rubros['gasto__municipio__id'] = municipio_id

        # obtiene datos comparativo de todos los años
        inicial = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio,
                                                   gasto__periodo=PERIODO_INICIAL,
                                                   subsubtipogasto__clasificacion=TipoGasto.CORRIENTE,).
                       values('gasto__anio', 'gasto__periodo').annotate(asignado=Sum('asignado')).order_by())
        final = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio,
                                                 gasto__periodo=PERIODO_FINAL,
                                                 subsubtipogasto__clasificacion=TipoGasto.CORRIENTE,).values('gasto__anio',
                                                                                                             'gasto__periodo').annotate(ejecutado=Sum('ejecutado')).order_by())
        anual2 = glue(inicial=inicial, final=final, key='gasto__anio')
        clase_sql = "SELECT core_gasto.anio AS gasto__anio,'{periodo}' AS gasto__periodo,SUM({quesumar}) AS clase FROM core_gastodetalle JOIN core_gasto ON core_gastodetalle.gasto_id=core_gasto.id \
        JOIN lugar_clasificacionmunicano ON core_gasto.municipio_id=lugar_clasificacionmunicano.municipio_id AND \
        core_gasto.anio=lugar_clasificacionmunicano.anio JOIN core_subsubtipogasto ON core_gastodetalle.subsubtipogasto_id=core_subsubtipogasto.codigo \
        WHERE core_gasto.periodo='{periodo}' AND core_subsubtipogasto.clasificacion={subsubtipogasto} \
        AND lugar_clasificacionmunicano.clasificacion_id=(SELECT clasificacion_id FROM lugar_clasificacionmunicano WHERE municipio_id={municipio} AND lugar_clasificacionmunicano.anio=core_gasto.anio) \
        GROUP BY core_gasto.anio"
        sql = clase_sql.format(quesumar='asignado', municipio=municipio_id,
                               periodo=PERIODO_INICIAL, subsubtipogasto=TipoGasto.CORRIENTE, )
        cursor = connection.cursor()
        cursor.execute(sql)
        inicial_clase = dictfetchall(cursor)
        sql = clase_sql.format(quesumar='ejecutado', municipio=municipio_id,
                               periodo=PERIODO_FINAL, subsubtipogasto=TipoGasto.CORRIENTE, )
        cursor = connection.cursor()
        cursor.execute(sql)
        final_clase = dictfetchall(cursor)
        for row in anual2:
            found = False
            for row2 in inicial_clase:
                if row2['gasto__anio'] == row['gasto__anio']:
                    found = True
                    try:
                        row['clase_inicial'] = row2['clase'] / \
                            mi_clase_anios_count[row['gasto__anio']]
                    except KeyError:
                        row['clase_inicial'] = 0
            if not found:
                row['clase_inicial'] = 0
        for row in anual2:
            found = False
            for row2 in final_clase:
                if row2['gasto__anio'] == row['gasto__anio']:
                    found = True
                    try:
                        row['clase_final'] = row2['clase'] / \
                            mi_clase_anios_count[row['gasto__anio']]
                    except KeyError:
                        row['clase_final'] = 0
            if not found:
                row['clase_final'] = 0
        comparativo_anios = anual2

        # comparativo con promedio de clasificacion para un año específico
        inicial = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL,
                                                   gasto__anio=year, subsubtipogasto__clasificacion=TipoGasto.CORRIENTE, gasto__municipio__slug=municipio).
                       values('gasto__periodo').annotate(municipio=Sum('asignado')))
        actualizado = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_ACTUALIZADO,
                                                       gasto__anio=year, subsubtipogasto__clasificacion=TipoGasto.CORRIENTE, gasto__municipio__slug=municipio).
                           values('gasto__periodo').annotate(municipio=Sum('ejecutado')))
        final = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL,
                                                 gasto__anio=year, subsubtipogasto__clasificacion=TipoGasto.CORRIENTE, gasto__municipio__slug=municipio).
                     values('gasto__periodo').annotate(municipio=Sum('ejecutado')))

        # obtiene datos para municipios de la misma clase
        inicial_clase = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_INICIAL,
                                                    subsubtipogasto__clasificacion=TipoGasto.CORRIENTE,
                                                    gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, gasto__municipio__clase__anio=year).\
            values('gasto__periodo').order_by('gasto__periodo').annotate(clase=Sum('asignado'))
        actualizado_clase = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_ACTUALIZADO,
                                                        subsubtipogasto__clasificacion=TipoGasto.CORRIENTE,
                                                        gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, gasto__municipio__clase__anio=year).\
            values('gasto__periodo').order_by('gasto__periodo').annotate(clase=Sum('ejecutado'))
        final_clase = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_FINAL,
                                                  subsubtipogasto__clasificacion=TipoGasto.CORRIENTE,
                                                  gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, gasto__municipio__clase__anio=year).\
            values('gasto__periodo').order_by('gasto__periodo').annotate(clase=Sum('ejecutado'))

        # obtiene totales
        total_municipio_inicial = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_INICIAL, gasto__municipio__slug=municipio).\
            aggregate(total=Sum('asignado'))['total']
        total_municipio_final = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_FINAL, gasto__municipio__slug=municipio).\
            aggregate(total=Sum('ejecutado'))['total']
        total_clase_inicial = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_INICIAL,
                                                          gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, gasto__municipio__clase__anio=year).\
            aggregate(total=Sum('asignado'))['total']
        total_clase_final = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=PERIODO_FINAL,
                                                        gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, gasto__municipio__clase__anio=year).\
            aggregate(total=Sum('ejecutado'))['total']

        # inserta datos para municipio de la misma clase
        if inicial:
            inicial[0]['clase'] = inicial_clase[0]['clase'] / mi_clase_count
            inicial[0]['claseraw'] = inicial_clase[0]['clase']
            inicial[0]['clasep'] = inicial_clase[0]['clase'] / total_clase_inicial * 100
            inicial[0]['municipiop'] = inicial[0]['municipio'] / total_municipio_inicial * 100
        if actualizado:
            actualizado[0]['clase'] = actualizado_clase[0]['clase'] / mi_clase_count
            actualizado[0]['claseraw'] = actualizado_clase[0]['clase']
            actualizado[0]['clasep'] = 0  # Does it need FIXME?
            actualizado[0]['municipiop'] = 0  # Does it need FIXME?
        if final:
            final[0]['clase'] = final_clase[0]['clase'] / mi_clase_count
            final[0]['claseraw'] = final_clase[0]['clase']
            final[0]['clasep'] = final_clase[0]['clase'] / total_clase_final * 100
            final[0]['municipiop'] = final[0]['municipio'] / total_municipio_final * 100
        comparativo3 = list(chain(inicial, actualizado, final))
        comparativo2 = list(chain(inicial, final, ))

        for d in comparativo3:
            d.update((k, PERIODO_VERBOSE[v]) for k, v in d.iteritems() if k == "gasto__periodo")

        gasto_promedio = GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL,
                                                     subsubtipogasto__clasificacion=TipoGasto.CORRIENTE,
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
                                                   subsubtipogasto__clasificacion=TipoGasto.CORRIENTE, gasto__municipio__slug=municipio).\
            values('gasto__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_barra_final = source_barra  # FIXME este es un work-around

        # chart: porcentage gastos de funcionamiento
        source_pgf_asignado = GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio,
                                                          gasto__periodo=periodo, subsubtipogasto__clasificacion=TipoGasto.CORRIENTE).aggregate(asignado=Sum(quesumar))
        source_pgf_asignado['nombre'] = 'Funcionamiento'
        otros_asignado = GastoDetalle.objects.filter(gasto__anio=year, gasto__municipio__slug=municipio, gasto__periodo=periodo).exclude(
            subsubtipogasto__clasificacion=TipoGasto.CORRIENTE).aggregate(asignado=Sum(quesumar))
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
                                                   subsubtipogasto__clasificacion=TipoGasto.CORRIENTE,).values(
            'gasto__anio', 'gasto__periodo').annotate(asignado=Sum('asignado')).order_by())
        final = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL,
                                                 subsubtipogasto__clasificacion=TipoGasto.CORRIENTE,).values(
            'gasto__anio', 'gasto__periodo').annotate(ejecutado=Sum('ejecutado')).order_by())
        anual2 = glue(inicial=inicial, final=final, key='gasto__anio')

        # grafico de ejecutado y asignado a nivel nacional (distintas clases)
        sql_tpl = "SELECT clasificacion,\
                (SELECT SUM(asignado) AS {asignado} FROM core_GastoDetalle JOIN core_Gasto ON core_GastoDetalle.gasto_id=core_Gasto.id JOIN core_SubSubTipoGasto ON core_GastoDetalle.subsubtipogasto_id=core_SubSubTipoGasto.codigo \
                JOIN lugar_clasificacionmunicano ON core_Gasto.municipio_id=lugar_clasificacionmunicano.municipio_id AND core_Gasto.anio=lugar_clasificacionmunicano.anio \
                WHERE core_Gasto.anio={year} AND core_Gasto.periodo='{periodo}' AND core_subsubtipogasto.clasificacion={subsubtipogasto} AND lugar_clasificacionmunicano.clasificacion_id=clase.id ), \
                (SELECT SUM(ejecutado) AS {ejecutado} FROM core_GastoDetalle JOIN core_Gasto ON core_GastoDetalle.gasto_id=core_Gasto.id JOIN core_SubSubTipoGasto ON core_GastoDetalle.subsubtipogasto_id=core_SubSubTipoGasto.codigo \
                JOIN lugar_clasificacionmunicano ON core_Gasto.municipio_id=lugar_clasificacionmunicano.municipio_id AND core_Gasto.anio=lugar_clasificacionmunicano.anio \
                WHERE core_Gasto.anio={year} AND core_Gasto.periodo='{periodo}' AND core_SubSubTipogasto.clasificacion={subsubtipogasto} AND lugar_clasificacionmunicano.clasificacion_id=clase.id ) \
                FROM lugar_clasificacionmunic AS clase ORDER BY clasificacion"
        sql = sql_tpl.format(asignado="inicial_asignado", ejecutado="inicial_ejecutado",
                             year=year, periodo=PERIODO_INICIAL, subsubtipogasto=TipoGasto.CORRIENTE, )
        cursor = connection.cursor()
        cursor.execute(sql)
        inicial = dictfetchall(cursor)
        sql = sql_tpl.format(asignado="final_asignado", ejecutado="final_ejecutado",
                             year=year, periodo=PERIODO_FINAL, subsubtipogasto=TipoGasto.CORRIENTE, )
        cursor = connection.cursor()
        cursor.execute(sql)
        final = dictfetchall(cursor)
        sql = sql_tpl.format(asignado="actualizado_asignado", ejecutado="actualizado_ejecutado",
                             year=year, periodo=PERIODO_ACTUALIZADO, subsubtipogasto=TipoGasto.CORRIENTE, )
        cursor = connection.cursor()
        cursor.execute(sql)
        actualizado = dictfetchall(cursor)
        sql = sql_tpl.format(asignado="asignado", ejecutado="ejecutado",
                             year=year, periodo=periodo, subsubtipogasto=TipoGasto.CORRIENTE, )
        cursor = connection.cursor()
        cursor.execute(sql)
        porclase_periodo = dictfetchall(cursor)
        #porclase = glue(inicial, final, 'clasificacion', actualizado=actualizado)
        porclase = superglue(data=(inicial, final, actualizado,
                                   porclase_periodo), key='clasificacion')
        for d in porclase:
            if d['asignado'] and d['ejecutado']:
                d['nivel'] = d['ejecutado'] / d['asignado'] * 100
            else:
                d['nivel'] = 0

        # grafico de ejecutado y asignado a nivel nacional (distintas clases) porcentage
        sql_tpl = "SELECT clasificacion,\
                (SELECT SUM(asignado) FROM core_gastodetalle cgd\
                JOIN core_gasto cg ON cgd.gasto_id=cg.id \
                JOIN core_subsubtipogasto sstg ON cgd.subsubtipogasto_id=sstg.codigo \
                JOIN lugar_clasificacionmunicano lcma ON cg.municipio_id=lcma.municipio_id \
                AND cg.anio=lcma.anio \
                WHERE cg.anio={year} AND cg.periodo='{periodo}' \
                AND sstg.clasificacion={subsubtipogasto} \
                AND lcma.clasificacion_id=clase.id) AS {asignado},\
                (SELECT SUM(asignado) FROM core_gastodetalle cgd\
                JOIN core_gasto cg ON cgd.gasto_id=cg.id \
                JOIN core_subsubtipogasto sstg ON cgd.subsubtipogasto_id=sstg.codigo \
                JOIN lugar_clasificacionmunicano lcma ON cg.municipio_id=lcma.municipio_id \
                AND cg.anio=lcma.anio \
                WHERE cg.anio={year} AND cg.periodo='{periodo}' \
                AND sstg.clasificacion={subsubtipogasto} \
                AND lcma.clasificacion_id=clase.id) /\
                (SELECT SUM(asignado) FROM core_gastodetalle as cgd \
                JOIN core_gasto as cg ON cgd.gasto_id=cg.id \
                JOIN core_subsubtipogasto as sstg ON cgd.subsubtipogasto_id=sstg.codigo \
                JOIN lugar_clasificacionmunicano lcma ON cg.municipio_id=lcma.municipio_id \
                AND cg.anio=lcma.anio \
                WHERE cg.anio={year} \
                AND cg.periodo='{periodo}' \
                AND lcma.clasificacion_id=clase.id \
                HAVING SUM(asignado)>0) * 100 \
                AS {asignado}_porcentaje,\
                (SELECT SUM(ejecutado) FROM core_gastodetalle cgd\
                JOIN core_gasto cg ON cgd.gasto_id=cg.id \
                JOIN core_subsubtipogasto sstg ON cgd.subsubtipogasto_id=sstg.codigo \
                JOIN lugar_clasificacionmunicano lcma ON cg.municipio_id=lcma.municipio_id \
                AND cg.anio=lcma.anio \
                WHERE cg.anio={year} \
                AND cg.periodo='{periodo}' \
                AND sstg.clasificacion={subsubtipogasto} \
                AND lcma.clasificacion_id=clase.id) as {ejecutado},\
                (SELECT SUM(ejecutado) FROM core_gastodetalle cgd\
                JOIN core_gasto cg ON cgd.gasto_id=cg.id \
                JOIN core_subsubtipogasto sstg ON cgd.subsubtipogasto_id=sstg.codigo \
                JOIN lugar_clasificacionmunicano lcma ON cg.municipio_id=lcma.municipio_id \
                AND cg.anio=lcma.anio \
                WHERE cg.anio={year} \
                AND cg.periodo='{periodo}' \
                AND sstg.clasificacion={subsubtipogasto} \
                AND lcma.clasificacion_id=clase.id) /\
                (SELECT SUM(ejecutado) FROM core_gastodetalle cgd\
                JOIN core_gasto cg ON cgd.gasto_id=cg.id \
                JOIN core_subsubtipogasto sstg ON cgd.subsubtipogasto_id=sstg.codigo \
                JOIN lugar_clasificacionmunicano lcma ON cg.municipio_id=lcma.municipio_id \
                AND cg.anio=lcma.anio \
                WHERE cg.anio={year} \
                AND cg.periodo='{periodo}' \
                AND lcma.clasificacion_id=clase.id \
                HAVING SUM(ejecutado)>0) * 100 \
                AS {ejecutado}_porcentaje\
                FROM lugar_clasificacionmunic AS clase ORDER BY clasificacion"
        sql = sql_tpl.format(asignado="inicial_asignado", ejecutado='inicial_ejecutado',
                             year=year, periodo=PERIODO_INICIAL, subsubtipogasto=TipoGasto.CORRIENTE)
        cursor = connection.cursor()
        cursor.execute(sql)
        inicial = dictfetchall(cursor)
        sql = sql_tpl.format(asignado="final_asignado", ejecutado="final_ejecutado",
                             year=year, periodo=PERIODO_FINAL, subsubtipogasto=TipoGasto.CORRIENTE)
        cursor = connection.cursor()
        cursor.execute(sql)
        final = dictfetchall(cursor)
        sql = sql_tpl.format(asignado="asignado", ejecutado="ejecutado",
                             year=year, periodo=periodo, subsubtipogasto=TipoGasto.CORRIENTE)
        cursor = connection.cursor()
        cursor.execute(sql)
        porclasep_periodo = dictfetchall(cursor)
        sql = sql_tpl.format(asignado="final_asignado", ejecutado="final_ejecutado",
                             year=year, periodo=PERIODO_FINAL, subsubtipogasto=TipoGasto.CORRIENTE)
        cursor = connection.cursor()
        cursor.execute(sql)
        final = dictfetchall(cursor)
        sql = sql_tpl.format(asignado="actualizado_asignado", ejecutado="actualizado_ejecutado",
                             year=year, periodo=PERIODO_ACTUALIZADO, subsubtipogasto=TipoGasto.CORRIENTE)
        cursor = connection.cursor()
        cursor.execute(sql)
        actualizado = dictfetchall(cursor)
        #porclasep = glue(inicial, final, 'clasificacion', actualizado=actualizado)
        porclasep = superglue(data=(inicial,
                                    porclasep_periodo,
                                    final,
                                    actualizado),
                              key='clasificacion')

        # indicando que cuentas debo exluir
        excluir_cuentas_rubros['subsubtipogasto__codigo__in'] = [TipoGasto.IMPREVISTOS,
                                                                 TipoGasto.TRANSFERENCIAS_CAPITAL]
        source_inicial = GastoDetalle.objects. \
            filter(gasto__periodo=PERIODO_INICIAL,
                   subsubtipogasto__clasificacion=TipoGasto.CORRIENTE). \
            order_by('gasto__anio'). \
            values('gasto__anio'). \
            annotate(ejecutado=Sum('ejecutado'),
                     asignado=Sum('asignado'))
        total_asignado_anio = GastoDetalle.objects. \
            filter(gasto__periodo=PERIODO_INICIAL,
                   gasto__anio=year). \
            order_by('gasto__anio'). \
            values('gasto__anio'). \
            annotate(asignado=Sum('asignado'))
        source_final = GastoDetalle.objects. \
            filter(gasto__periodo=periodo,
                   subsubtipogasto__clasificacion=TipoGasto.CORRIENTE). \
            order_by('gasto__anio'). \
            values('gasto__anio'). \
            annotate(ejecutado=Sum('ejecutado'),
                     asignado=Sum('asignado'))
        total_ejecutado_anio = GastoDetalle.objects. \
            filter(gasto__periodo=periodo,
                   gasto__anio=year). \
            order_by('gasto__anio'). \
            values('gasto__anio'). \
            annotate(ejecutado=Sum('ejecutado'))

        # obtiene valores para este año de las listas
        try:
            asignado = (item for item in source_inicial if item["gasto__anio"] == int(
                year)).next()['asignado']
            total_asignado = total_asignado_anio[0]['asignado']
            asignado_percent = percentage(asignado, total_asignado)
        except StopIteration:
            asignado = 0
        try:
            ejecutado = (item for item in source_final if item["gasto__anio"] == int(year)).next()[
                'ejecutado']
            total_ejecutado = total_ejecutado_anio[0]['ejecutado']
            ejecutado_percent = percentage(ejecutado, total_ejecutado)
        except StopIteration:
            ejecutado = 0
        source = glue(source_inicial, source_final, 'gasto__anio')

        # FIXME. en el grafico de periodos...  de donde tomar los datos?
        source_barra_inicial = GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL,
                                                           subsubtipogasto__clasificacion=TipoGasto.CORRIENTE).\
            values('gasto__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_barra_final = GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL,
                                                         subsubtipogasto__clasificacion=TipoGasto.CORRIENTE).\
            values('gasto__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

        # chart: porcentage gastos de funcionamiento
        source_pgf_asignado = GastoDetalle.objects.filter(
            gasto__anio=year, gasto__periodo=periodo, subsubtipogasto__clasificacion=TipoGasto.CORRIENTE).aggregate(asignado=Sum(quesumar))
        source_pgf_asignado['nombre'] = 'Funcionamiento'
        otros_asignado = GastoDetalle.objects.filter(gasto__anio=year, gasto__periodo=periodo).exclude(
            subsubtipogasto__clasificacion=TipoGasto.CORRIENTE).aggregate(asignado=Sum(quesumar))
        otros_asignado['nombre'] = 'Otros'
        source_pgf = [source_pgf_asignado, otros_asignado]

        # comparativo con promedio de clasificacion para un año específico
        inicial = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL,
                                                   gasto__anio=year, subsubtipogasto__clasificacion=TipoGasto.CORRIENTE, ).
                       order_by('gasto__periodo').values('gasto__periodo').annotate(municipio=Sum('asignado')))
        actualizado = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_ACTUALIZADO,
                                                       gasto__anio=year, subsubtipogasto__clasificacion=TipoGasto.CORRIENTE, ).
                           order_by('gasto__periodo').values('gasto__periodo').annotate(municipio=Sum('ejecutado')))
        final = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL,
                                                 gasto__anio=year, subsubtipogasto__clasificacion=TipoGasto.CORRIENTE, ).
                     order_by('gasto__periodo').values('gasto__periodo').annotate(municipio=Sum('ejecutado')))
        comparativo3 = list(chain(inicial, actualizado, final))
        comparativo2 = list(chain(inicial, final, ))
        for d in comparativo3:
            d.update((k, PERIODO_VERBOSE[v]) for k, v in d.iteritems() if k == "gasto__periodo")

        # obtiene datos comparativo de todos los años
        final = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL, subsubtipogasto__clasificacion=TipoGasto.CORRIENTE,).values(
            'gasto__anio', 'gasto__periodo').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')))
        comparativo_anios = final

    # obtiene datos de gastos en ditintos rubros de corriente (clasificacion 0)
    rubros_inicial = GastoDetalle.objects. \
        filter(**filtro_rubros). \
        filter(gasto__periodo=PERIODO_INICIAL). \
        exclude(**excluir_cuentas_rubros). \
        values('codigo__subsubtipogasto__origen_gc__id',
               'codigo__subsubtipogasto__origen_gc__nombre'). \
        order_by('codigo__subsubtipogasto__origen_gc__orden'). \
        annotate(inicial_asignado=Sum('asignado'))
    rubros_actualizado = GastoDetalle.objects. \
        filter(**filtro_rubros). \
        filter(gasto__periodo=PERIODO_ACTUALIZADO). \
        exclude(**excluir_cuentas_rubros). \
        values('codigo__subsubtipogasto__origen_gc__id',
               'codigo__subsubtipogasto__origen_gc__nombre'). \
        order_by('codigo__subsubtipogasto__origen_gc__orden'). \
        annotate(actualizado_asignado=Sum('asignado'),
                 actualizado_ejecutado=Sum('ejecutado'))
    rubros_final = GastoDetalle.objects. \
        filter(**filtro_rubros). \
        filter(gasto__periodo=PERIODO_FINAL). \
        exclude(**excluir_cuentas_rubros). \
        values('codigo__subsubtipogasto__origen_gc__id',
               'codigo__subsubtipogasto__origen_gc__nombre'). \
        order_by('codigo__subsubtipogasto__origen_gc__orden'). \
        annotate(final_asignado=Sum('asignado'),
                 final_ejecutado=Sum('ejecutado'))
    rubros_periodo = GastoDetalle.objects. \
        filter(**filtro_rubros). \
        filter(gasto__periodo=periodo). \
        exclude(**excluir_cuentas_rubros). \
        values('codigo__subsubtipogasto__origen_gc__id',
               'codigo__subsubtipogasto__origen_gc__nombre'). \
        order_by('codigo__subsubtipogasto__origen_gc__orden'). \
        annotate(asignado=Sum('asignado'),
                 ejecutado=Sum('ejecutado'))

    # rubros = glue(rubros_inicial, rubros_final, 'subsubtipogasto__codigo', actualizado=rubros_actualizado)
    rubros = superglue(data=(rubros_inicial,
                             rubros_final,
                             rubros_actualizado,
                             rubros_periodo),
                       key='codigo__subsubtipogasto__origen_gc__id')

    #
    # chartit!
    #
    if municipio:
        gf_comparativo_anios = RawDataPool(
            series=[{'options': {'source': comparativo_anios},
                     'names':  [u'Años', u'gasto__periodo', u'P. Inicial', u'Ejecutado', u'Categoría Inicial %s' % (mi_clase.clasificacion,), u'Categoría Final %s' % (mi_clase.clasificacion,)],
                     'terms':  ['gasto__anio', 'gasto__periodo', 'asignado', 'ejecutado', 'clase_inicial', 'clase_final'],
                     }],
        )
        gf_comparativo_anios_column = Chart(
            datasource=gf_comparativo_anios,
            series_options=[{'options': {
                'type': 'column',
                'stacking': False},
                'terms': {
                'gasto__anio': ['asignado', 'ejecutado', 'clase_inicial', 'clase_final'],
            },
            }],
            chart_options={'title': {'text': ' '}},
        )
        gf_comparativo3 = RawDataPool(
            series=[{'options': {'source': comparativo3},
                     'names':  [u'Gastos', u'Municipio', u'Categoría %s' % (mi_clase.clasificacion,)],
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
            chart_options={
                'title': {'text': ' '},
                # 'subtitle': { 'text': u'Municipio de %s y Categoría del Municipio %s' % (municipio_row.nombre, year)},
                'yAxis': {'title': {'text': u'Millones de córdobas'}},
            },
        )
        gf_comparativo2 = RawDataPool(
            series=[{'options': {'source': comparativo2},
                     'names': [u'Gastos', u'Municipio', u'Categoría %s' % (mi_clase.clasificacion,), ],
                     'terms':  ['gasto__periodo', 'municipiop', 'clasep'],
                     }],
            #sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
        )
        gf_comparativo2_column = Chart(
            datasource=gf_comparativo2,
            series_options=[{'options': {
                'type': 'column',
                'stacking': False},
                'terms': {
                'gasto__periodo': ['municipiop', 'clasep']
            },
            }],
            chart_options={
                'title': {'text': ' '},
                'subtitle': {'text': u' '},
                'tooltip': {'pointFormat': '{series.name}: <b>{point.y:.2f}%</b>'},
                'yAxis': {'title': {'text': u'Millones de córdobas'}},
                'xAxis': {'title': {'text': u'Gastos de funcionamiento'}},
            },
        )
    else:  # chartit no municipio
        gf_nivelejecucion = RawDataPool(
            series=[{'options': {'source': porclase},
                     'terms':  ['clasificacion', 'ejecutado', 'asignado', 'nivel'],
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
                'title': {'text': u'Nivel de ejecución %s' % (year,)},
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

    data_pgf = RawDataPool(
        series=[{
            'options': {'source': source_pgf},
            'terms': ['nombre', 'asignado', ]
        }]
    )
    data_rubros = RawDataPool(
        series=[{
            'options': {'source': rubros},
            'terms': ['subsubtipogasto__nombre', datacol]
        }]
    )
    pie = Chart(
        datasource=data_rubros,
        series_options=[{
            'options': {'type': 'pie'},
            'terms': {'subsubtipogasto__nombre': [datacol]}
        }],
        chart_options=chart_options)

    bar = Chart(
        datasource=data_rubros,
        series_options=[
            {
                'options': {
                    'type': 'column',
                    'colorByPoint': True,
                },
                'terms': {
                    'subsubtipogasto__nombre': [datacol]
                }
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
            'pointFormat': '<span>Presupuesto Inicial</span>:<b>{point.y}</b>',
            'interval': 10
        }
        bar_horizontal = graphChart(parameters)
    elif porclasep:
        parameters = {
            'data': porclasep,
            'field1': 'clasificacion',
            'field2': '{}_porcentaje'.format(quesumar),
            'typechart': 'column',
            'title': 'Porcentaje del Gasto Total',
            'labelX_axis': 'Grupos',
            'labelY_axis': 'Porcentaje',
            'pointFormat': '<span>{series.name}</span>:<b>{point.y:.2f}%</b>',
            'interval': 10
        }
        bar_horizontal = graphChart(parameters)

    portada = False #FIXME: convert to view
    if portada:
        charts = (pie,)
    elif bar_horizontal:
        charts = (bar_horizontal)
    else:
        charts = (pie, bar)

    porano_table = historial_gastos_corrientes(periodo_list, year, municipio_id)
    # Bubble tree data
    bubble_source = aci_bubbletree_data_gasto(municipio, year, portada)

    reporte = request.POST.get("reporte", "")
    if "excel" in request.POST.keys() and reporte:
        from core.utils import obtener_excel_response

        data = {'charts': charts,
                'municipio': municipio_row,
                'municipio_list': municipio_list,
                'year_list': year_list,
                'otros': otros,
                'rubros': rubros,
                'anuales': anual2,
                'ejecutado': ejecutado,
                'asignado': asignado,
                'porclase': porclase,
                'porclasep': porclasep,
                'mi_clase': mi_clase,
                'year': year,
                'porano': porano_table,
                'asignado_percent': asignado_percent,
                'ejecutado_percent': ejecutado_percent}

        return obtener_excel_response(reporte=reporte, data=data)

    template_name = 'expenses.html'
    context = {
        'charts': charts,
        'municipio': municipio_row,
        'municipio_list': municipio_list,
        'year_list': year_list,
        'indicator_name': "Gastos de funcionamiento",
        'indicator': "gf",
        'mostraren': "porcentaje",
        'indicator_description': "Mide el porcentaje del presupuesto de gasto que el Municipio destina,"
                                 " para gastos de funcionamiento de la municipalidad. ",
        'otros': otros,
        'rubros': rubros,
        'anuales': anual2,
        'ejecutado': ejecutado,
        'asignado': asignado,
        'porclase': porclase,
        'bubble_data': bubble_source,
        'asignado_percent': asignado_percent,
        'ejecutado_percent': ejecutado_percent,
        'periodo_list': periodo_list,
        'porclasep': porclasep,
        'mi_clase': mi_clase,
        'porano': porano_table,
        'total_nacional_asignado': total_nacional_asignado,
        'total_nacional_ejecutado': total_nacional_ejecutado,
        'year': year}
    return render(request, template_name, context)
