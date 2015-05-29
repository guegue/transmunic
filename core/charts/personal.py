# -*- coding: utf-8 -*-
##############################################################################
#
# Gastos de personal charts /core/gpersonal
#
##############################################################################

from itertools import chain
from datetime import datetime, time

from django.db import connection
from django.db.models import Q, Sum, Max, Min, Avg, Count
from django.shortcuts import render_to_response
from django.template import RequestContext

from chartit import DataPool, Chart, PivotDataPool, PivotChart, RawDataPool

from core.models import IngresoDetalle, Ingreso, GastoDetalle, Gasto, Inversion, Proyecto, Municipio, TipoGasto, InversionFuente, InversionFuenteDetalle, CatInversion, ClasificacionMunicAno
from core.models import Anio, getYears, dictfetchall, glue
from core.models import PERIODO_INICIAL, PERIODO_ACTUALIZADO, PERIODO_FINAL, PERIODO_VERBOSE


def gpersonal_chart(request):
    municipio_list = Municipio.objects.all()
    municipio = request.GET.get('municipio', None)
    year_list = getYears(Gasto)
    year = request.GET.get('year', None)
    if not year:
        year = year_list[-2]

    periodo = Anio.objects.get(anio=year).periodo
    quesumar = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'

    from collections import OrderedDict #FIXME move up
    if municipio:
        municipio_id = Municipio.objects.get(slug=municipio).id
        source_inicial = GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL, \
            tipogasto=TipoGasto.PERSONAL, gasto__municipio__slug=municipio).\
            values('gasto__year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_final = GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL, \
            tipogasto=TipoGasto.PERSONAL, gasto__municipio__slug=municipio).\
            values('gasto__year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

        # obtiene datos para grafico comparativo de tipo de gastos
        tipo_inicial= list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__year=year, gasto__periodo=PERIODO_INICIAL, tipogasto=TipoGasto.PERSONAL).values('subtipogasto__nombre').annotate(asignado=Sum('asignado')))
        tipo_final = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__year=year, gasto__periodo=PERIODO_FINAL, tipogasto=TipoGasto.PERSONAL).values('subtipogasto__nombre').annotate(ejecutado=Sum('ejecutado')))
        tipo = glue(tipo_inicial, tipo_final, periodo, 'subtipogasto__nombre')

        # obtiene clase y contador (otros en misma clase) para este año
        mi_clase = ClasificacionMunicAno.objects.get(municipio__slug=municipio, anio=year)
        mi_clase_count = ClasificacionMunicAno.objects.filter(clasificacion__clasificacion=mi_clase.clasificacion, anio=year).count()
        # obtiene clase y contador (otros en misma clase) para todos los años
        mi_clase_anios = list(ClasificacionMunicAno.objects.filter(municipio__slug=municipio).values('anio', 'clasificacion__clasificacion').annotate())
        mi_clase_anios_count = {}
        for aclase in mi_clase_anios:
            mi_clase_anios_count[aclase['anio']] = ClasificacionMunicAno.objects.filter(clasificacion__clasificacion=aclase['clasificacion__clasificacion'], anio=aclase['anio']).count()

        # obtiene datos comparativo de todos los años
        #inicial = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL, tipogasto=TipoGasto.PERSONAL,).values('gasto__year', 'gasto__periodo').annotate(municipio_inicial=Sum('asignado')))
        final = list(GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_FINAL, tipogasto=TipoGasto.PERSONAL,).values('gasto__year', 'gasto__periodo').annotate(municipio_final=Sum('ejecutado')))
        # obtiene datos para municipio de la misma clase
        #inicial_clase = GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL, tipogasto=TipoGasto.PERSONAL, \
        #        gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, gasto__municipio__clase__anio=year).\
        #        values('gasto__year','gasto__periodo').order_by('gasto__periodo').annotate(clase_inicial=Sum('asignado'))
        final_clase_sql = "SELECT year AS gasto__year,'F' AS gasto__periodo,SUM(ejecutado) AS clase_final FROM core_gastodetalle JOIN core_gasto ON core_gastodetalle.gasto_id=core_gasto.id \
        JOIN lugar_clasificacionmunicano ON core_gasto.municipio_id=lugar_clasificacionmunicano.municipio_id AND \
        core_gasto.year=lugar_clasificacionmunicano.anio JOIN core_tipogasto ON core_gastodetalle.tipogasto_id=core_tipogasto.codigo \
        WHERE core_gasto.periodo=%s AND core_tipogasto.codigo=%s \
        AND lugar_clasificacionmunicano.clasificacion_id=(SELECT clasificacion_id FROM lugar_clasificacionmunicano WHERE municipio_id=%s AND lugar_clasificacionmunicano.anio=core_gasto.year) \
        GROUP BY year"
        cursor = connection.cursor()
        cursor.execute(final_clase_sql, [PERIODO_FINAL, TipoGasto.PERSONAL, municipio_id])
        final_clase = dictfetchall(cursor)
        # inserta datos para municipio de la misma clase
        #for row in inicial:
        #    for row2 in inicial_clase:
        #        if row2['gasto__year'] == row['gasto__year']:
        #            row['clase_inicial'] = row2['clase_inicial'] / mi_clase_anios_count[row['gasto__year']]
        for row in final:
            found = False
            for row2 in final_clase:
                if row2['gasto__year'] == row['gasto__year']:
                    found = True
                    try:
                        row['clase_final'] = row2['clase_final'] / mi_clase_anios_count[row['gasto__year']]
                    except KeyError:
                        row['clase_final'] = 0
            if not found:
                row['clase_final'] = 0
        #for row in inicial:
        #    found = False
        #    for row2 in final:
        #        if row2['gasto__year'] == row['gasto__year']:
        #            found = True
        #            row['clase_final'] = row2['clase_final'] / mi_clase_anios_count[row['gasto__year']]
        #            row['municipio_final'] = row2['municipio_final']
        #        if not found:
        #            row['clase_final'] = 0
        #            row['municipio_final'] = 0
        #comparativo_anios = inicial
        comparativo_anios = final

        # comparativo con promedio de clasificacion para un año específico
        inicial = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL, \
            gasto__year=year, tipogasto=TipoGasto.PERSONAL, gasto__municipio__slug=municipio).\
            values('gasto__periodo').annotate(municipio=Sum('asignado')))
        actualizado = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_ACTUALIZADO, \
            gasto__year=year, tipogasto=TipoGasto.PERSONAL, gasto__municipio__slug=municipio).\
            values('gasto__periodo').annotate(municipio=Sum('ejecutado')))
        final = list(GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL, \
            gasto__year=year, tipogasto=TipoGasto.PERSONAL, gasto__municipio__slug=municipio).\
            values('gasto__periodo').annotate(municipio=Sum('ejecutado')))

        # obtiene datos para municipio de la misma clase
        inicial_clase = GastoDetalle.objects.filter(gasto__year=year, gasto__periodo=PERIODO_INICIAL,\
                tipogasto=TipoGasto.PERSONAL, \
                gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, gasto__municipio__clase__anio=year).\
                values('gasto__periodo').order_by('gasto__periodo').annotate(clase=Sum('asignado'))
        actualizado_clase = GastoDetalle.objects.filter(gasto__year=year, gasto__periodo=PERIODO_ACTUALIZADO,\
                tipogasto=TipoGasto.PERSONAL, \
                gasto__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, gasto__municipio__clase__anio=year).\
                values('gasto__periodo').order_by('gasto__periodo').annotate(clase=Sum('ejecutado'))
        final_clase = GastoDetalle.objects.filter(gasto__year=year, gasto__periodo=PERIODO_FINAL,\
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
            values('gasto__year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        try:
            for record in source_inicial:
                record['ejecutado'] = source_final.filter(gasto__year=record['gasto__year'])[0]['ejecutado']
                record['promedio'] = gasto_promedio.filter(gasto__year=record['gasto__year'])[0]['asignado']
        except IndexError:
            record['promedio'] = 0 #FIXME: really?
            pass

        source = source_inicial
        #source = OrderedDict(sorted(source.items(), key=lambda t: t[0]))
            
        # FIXME. igual que abajo (sin municipio) de donde tomar los datos?
        source_barra = GastoDetalle.objects.filter( gasto__periodo=PERIODO_INICIAL, \
            tipogasto=TipoGasto.PERSONAL, gasto__municipio__slug=municipio).\
            values('gasto__year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_barra_final = source_barra # FIXME este es un work-around

        # chart: porcentage gastos de personal
        source_pgf_asignado =  GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL, tipogasto=TipoGasto.PERSONAL).aggregate(asignado=Sum('asignado'))
        source_pgf_asignado['nombre'] = 'Personal'
        otros_asignado = GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL).exclude(tipogasto=TipoGasto.PERSONAL).aggregate(asignado=Sum('asignado'))
        otros_asignado['nombre'] = 'Otros'
        source_pgf = [source_pgf_asignado, otros_asignado]
    else:
        municipio = ''
        source_inicial = GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL, \
            tipogasto=TipoGasto.PERSONAL).\
            values('gasto__year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_final = GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL, \
            tipogasto=TipoGasto.PERSONAL).\
            values('gasto__year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        for record in source_inicial:
            try:
                record['ejecutado'] = source_final.filter(gasto__year=record['gasto__year'])[0]['ejecutado']
            except IndexError:
                record['ejecutado'] = 0
        source = source_inicial

        # obtiene datos para grafico comparativo de tipo de gastos
        tipo_inicial= list(GastoDetalle.objects.filter(gasto__year=year, gasto__periodo=PERIODO_INICIAL).values('subtipogasto__nombre').annotate(asignado=Sum('asignado')))
        tipo_final = list(GastoDetalle.objects.filter(gasto__year=year, gasto__periodo=PERIODO_FINAL).values('subtipogasto__nombre').annotate(ejecutado=Sum('ejecutado')))
        tipo = glue(tipo_inicial, tipo_final, periodo, 'subtipogasto__nombre')

        # FIXME. en el grafico de periodos...  de donde tomar los datos?
        source_barra_inicial = GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL, \
            tipogasto=TipoGasto.PERSONAL).\
            values('gasto__year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_barra_final = GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL, \
            tipogasto=TipoGasto.PERSONAL).\
            values('gasto__year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

        # chart: porcentage gastos de personal
        source_pgf_asignado =  GastoDetalle.objects.filter(gasto__year=year, gasto__periodo=PERIODO_INICIAL, tipogasto=TipoGasto.PERSONAL).aggregate(asignado=Sum('asignado'))
        source_pgf_asignado['nombre'] = 'Personal'
        otros_asignado = GastoDetalle.objects.filter(gasto__year=year, gasto__periodo=PERIODO_INICIAL).exclude(tipogasto=TipoGasto.PERSONAL).aggregate(asignado=Sum('asignado'))
        otros_asignado['nombre'] = 'Otros'
        source_pgf = [source_pgf_asignado, otros_asignado]

    #
    # chartit!
    #
    if municipio:
        gf_comparativo_anios = RawDataPool(
            series=
                [{'options': {'source': comparativo_anios },
                'terms':  ['gasto__year','gasto__periodo','municipio_final','clase_final'],
                }],
            )
        gf_comparativo_anios_column = Chart(
                datasource = gf_comparativo_anios,
                series_options =
                [{'options':{
                    'type': 'column',
                    'stacking': False},
                    'terms':{
                    'gasto__year': ['municipio_final', 'clase_final'],
                    },
                    }],
                chart_options =
                {'title': { 'text': 'Gastos %s' % (municipio,)}},
                )
        gf_comparativo3 = RawDataPool(
            series=
                [{'options': {'source': comparativo3 },
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
                {'title': { 'text': 'Gastos %s %s' % (municipio, year)}},
                )
        gf_comparativo2 = RawDataPool(
            series=
                [{'options': {'source': comparativo2 },
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
                {'title': { 'text': 'Gastos %s %s' % (municipio, year)}},
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
                'title': { 'text': 'Gastos por tipo origen %s %s' % (year, municipio,)},
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
                'title': {'text': 'Gastos de personal %s %s ' % (municipio, year,)},
                'options3d': { 'enabled': 'true',  'alpha': '45', 'beta': '0' },
                'plotOptions': { 'pie': { 'dataLabels': { 'enabled': False }, 'showInLegend': True, 'depth': 35}},
                'tooltip': { 'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>' },
            },
    )
    data_barra = DataPool(
           series = [{
              'options': {'source': source_barra_final },
              'terms': [ 'gasto__year', 'ejecutado', 'asignado', ]
            }]
    )

    barra = Chart(
            datasource = data_barra,
            series_options =
              [{'options':{
                  'type': 'column',},
                'terms':{
                  'gasto__year': [
                    'asignado',
                    'ejecutado']
                  }}],
            chart_options = {
                'title': {'text': 'Gastos de personal %s ' % (municipio,)},
                'options3d': { 'enabled': 'true',  'alpha': 0, 'beta': 0, 'depth': 50 },
                },
            )
    if municipio:
        dataterms = ['gasto__year', 'asignado', 'ejecutado', 'promedio']
        terms = ['asignado', 'ejecutado', 'promedio',]
    else:
        municipio = ''
        dataterms = ['gasto__year', 'asignado', 'ejecutado']
        terms = ['asignado', 'ejecutado']

    data = RawDataPool(series = [{'options': {'source': source }, 'terms': dataterms}])
    gfbar = Chart(
            datasource = data,
            series_options = [{'options': {'type': 'column'}, 'terms': {'gasto__year': terms }}],
            chart_options = {
                'title': {'text': u'Gastos de personal año %s ' % (municipio,)},
                'options3d': { 'enabled': 'true',  'alpha': 0, 'beta': 0, 'depth': 50 },
                },
            #x_sortf_mapf_mts = (None, lambda i:  i.strftime('%Y'), False)
            )

    portada = False #FIXME: convert to view
    if portada:
        charts =  (pie, )
    elif municipio:
        charts =  (personal_tipo_column, gfbar, barra, pie, gf_comparativo2_column, gf_comparativo3_column, gf_comparativo_anios_column)
    else:
        charts =  (personal_tipo_column, gfbar, barra, pie)
    return render_to_response('gpersonal.html',{'charts': charts, 'municipio': municipio, 'municipio_list': municipio_list, 'year_list': year_list},\
        context_instance=RequestContext(request))
