# -*- coding: utf-8 -*-

from itertools import chain
from datetime import datetime, time

from django.db import connection
from django.db.models import Q, Sum, Max, Min, Avg, Count
from django.shortcuts import render_to_response
from django.template import RequestContext

from chartit import DataPool, Chart, PivotDataPool, PivotChart, RawDataPool

from core.models import IngresoDetalle, Ingreso, Proyecto, Inversion, Inversion, Proyecto, Municipio, TipoProyecto, InversionFuente, InversionFuenteDetalle, CatInversion, ClasificacionMunicAno
from core.models import Anio, getYears, dictfetchall, glue
from core.models import PERIODO_INICIAL, PERIODO_ACTUALIZADO, PERIODO_FINAL, PERIODO_VERBOSE, AREAGEOGRAFICA_VERBOSE

def inversion_chart(municipio=None):
    municipio_list = Municipio.objects.all()
    year_list = getYears(Inversion)

    if municipio:
        source = Proyecto.objects.filter(inversion__periodo=PERIODO_INICIAL, inversion__municipio__slug=municipio). \
            values('year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_ultimos = Proyecto.objects.filter(inversion__periodo=PERIODO_INICIAL, inversion__municipio__slug=municipio, \
            inversion__year__gt=list(year_list)[-3]). \
            values('inversion__year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
    else:
        municipio = ''
        source = Proyecto.objects.filter(inversion__periodo=PERIODO_INICIAL). \
            values('inversion__year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_ultimos = Proyecto.objects.filter(inversion__periodo=PERIODO_INICIAL, inversion__year__gt=list(year_list)[-3]). \
            values('inversion__year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

    data_ultimos = DataPool(
           series=
            [{'options': {
                'source': source_ultimos,
                'categories': 'inversion__year',
                },
              'terms': ['inversion__year', 'ejecutado', 'asignado',]
            }],
    )
    chart_ultimos = Chart(
            datasource = data_ultimos,
            series_options =
              [{'options':{
                  'type': 'bar',
                  'stacking': False},
                'terms': {'inversion__year': ['asignado', 'ejecutado']}
                }],
            chart_options =
              {'title': {'text': u'Inversión por últimos años %s' % (municipio, )}},
            #x_sortf_mapf_mts = (None, lambda i:  i.strftime('%Y'), False)
    )
    data = DataPool(
           series=
            [{'options': {
                'source': source,
                'categories': 'inversion__year',
                },
              'terms': ['inversion__year', 'ejecutado', 'asignado',]
            }],
    )
    chart = Chart(
            datasource = data,
            series_options =
              [{'options':{
                  'type': 'bar',
                  'stacking': False},
                'terms': {'inversion__year': ['asignado', 'ejecutado']}
                }],
            chart_options =
              {'title': {'text': u'Inversión por años %s' % (municipio, )}},
            #x_sortf_mapf_mts = (None, lambda i:  i.strftime('%Y'), False)
    )
    return {'charts': (chart, chart_ultimos), 'municipio_list': municipio_list}


##############################################################################
#
# Inversion charts /core/iversion-categoria FIXME: yep, mal nombre...
#
##############################################################################
def inversion_categoria_chart(municipio=None, year=None, portada=False):
    municipio_list = Municipio.objects.all()
    year_list = getYears(Inversion)
    if not year:
        year = year_list[-1]

    periodo = Anio.objects.get(anio=year).periodo
    quesumar = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'

    ChartError = False

    if municipio:
        municipio_id = Municipio.objects.get(slug=municipio).id
        source_ultimos = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__year__gt=year_list[-3]). \
            values('inversion__year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

        # tabla2, tabla3
        cat_inicial = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__periodo=PERIODO_INICIAL, inversion__year=year).values('catinversion__nombre').annotate(asignado=Sum('asignado')).order_by('catinversion')
        cat_actualizado = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__periodo=PERIODO_ACTUALIZADO, inversion__year=year).values('catinversion__nombre').annotate(ejecutado=Sum('ejecutado')).order_by('catinversion')
        cat_final = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__periodo=PERIODO_FINAL, inversion__year=year).values('catinversion__nombre').annotate(ejecutado=Sum('ejecutado')).order_by('catinversion')
        cat2 = glue(inicial=cat_inicial, final=cat_final, periodo=periodo, campo='catinversion__nombre')
        cat3 = glue(inicial=cat_inicial, final=cat_final, actualizado=cat_actualizado, periodo=periodo, campo='catinversion__nombre')

        # tabla4
        anual_inicial = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__periodo=PERIODO_INICIAL).values('inversion__year').annotate(asignado=Sum('asignado')).order_by('inversion__year')
        anual_actualizado = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__periodo=PERIODO_ACTUALIZADO).values('inversion__year').annotate(ejecutado=Sum('ejecutado')).order_by('inversion__year')
        anual_final = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__periodo=PERIODO_FINAL).values('inversion__year').annotate(ejecutado=Sum('ejecutado')).order_by('inversion__year')
        anual2 = glue(inicial=anual_inicial, final=anual_final, periodo=periodo, campo='inversion__year')
        anual3 = glue(inicial=anual_inicial, final=anual_final, actualizado=anual_actualizado, periodo=periodo, campo='inversion__year')

        # obtiene clase y contador (otros en misma clase) para este año
        mi_clase = ClasificacionMunicAno.objects.get(municipio__slug=municipio, anio=year)
        mi_clase_count = ClasificacionMunicAno.objects.filter(clasificacion__clasificacion=mi_clase.clasificacion, anio=year).count()
        # obtiene clase y contador (otros en misma clase) para todos los años
        mi_clase_anios = list(ClasificacionMunicAno.objects.filter(municipio__slug=municipio).values('anio', 'clasificacion__clasificacion').annotate())
        mi_clase_anios_count = {}
        for aclase in mi_clase_anios:
            mi_clase_anios_count[aclase['anio']] = ClasificacionMunicAno.objects.filter(clasificacion__clasificacion=aclase['clasificacion__clasificacion'], anio=aclase['anio']).count()

        # source base
        source = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__year=year, inversion__periodo=periodo).values('catinversion__nombre').annotate(ejecutado=Sum(quesumar)).order_by('catinversion')
        source_clase = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__year=year, inversion__periodo=periodo,\
                inversion__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, inversion__municipio__clase__anio=year).\
                values('catinversion__nombre').annotate(clase=Sum(quesumar))


        # obtiene datos para grafico comparativo de tipo de inversions
        tipo_inicial= list(Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__year=year, inversion__periodo=PERIODO_INICIAL).values('catinversion__nombre').annotate(asignado=Sum('asignado')))
        tipo_final = list(Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__year=year, inversion__periodo=PERIODO_FINAL).values('catinversion__nombre').annotate(ejecutado=Sum('ejecutado')))
        tipo = glue(inicial=tipo_inicial, final=tipo_final, periodo=periodo, campo='catinversion__nombre')

        # obtiene datos para grafico comparativo por area
        area_inicial= list(Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__year=year, inversion__periodo=PERIODO_INICIAL).values('areageografica').annotate(asignado=Sum('asignado')))
        area_final = list(Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__year=year, inversion__periodo=PERIODO_FINAL).values('areageografica').annotate(ejecutado=Sum('ejecutado')))
        area = glue(area_inicial, area_final, periodo, 'areageografica')

        # obtiene datos para grafico comparativo por fuente
        fuente_inicial = list(InversionFuenteDetalle.objects.filter(inversionfuente__municipio__slug=municipio, inversionfuente__year=year, inversionfuente__periodo=PERIODO_INICIAL).values('fuente__nombre').annotate(asignado=Sum('asignado')))
        fuente_final = list(InversionFuenteDetalle.objects.filter(inversionfuente__municipio__slug=municipio, inversionfuente__year=year, inversionfuente__periodo=PERIODO_FINAL).values('fuente__nombre').annotate(ejecutado=Sum('ejecutado')))
        fuente = glue(fuente_inicial, fuente_final, periodo, 'fuente__nombre')
        fuente_actual = list(InversionFuenteDetalle.objects.filter(inversionfuente__municipio__slug=municipio, inversionfuente__year=year, inversionfuente__periodo=periodo).values('fuente__nombre').annotate(ejecutado=Sum(quesumar)))

        # obtiene datos para OIM comparativo de todos los años
        inicial = list(Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__periodo=PERIODO_INICIAL).values('inversion__year', 'inversion__periodo').annotate(municipio_inicial=Sum('asignado')))
        final = list(Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__periodo=PERIODO_FINAL).values('inversion__year', 'inversion__periodo').annotate(municipio_final=Sum('ejecutado')))

        # obtiene datos para municipio de la misma clase de todos los años
        inicial_clase_sql = "SELECT year AS inversion__year,SUM(asignado) AS clase_inicial FROM core_proyecto JOIN core_inversion ON core_proyecto.inversion_id=core_inversion.id \
        JOIN lugar_clasificacionmunicano ON core_inversion.municipio_id=lugar_clasificacionmunicano.municipio_id AND \
        core_inversion.year=lugar_clasificacionmunicano.anio WHERE core_inversion.periodo=%s \
        AND lugar_clasificacionmunicano.clasificacion_id=(SELECT clasificacion_id FROM lugar_clasificacionmunicano WHERE municipio_id=%s AND lugar_clasificacionmunicano.anio=core_inversion.year) \
        GROUP BY year"
        cursor = connection.cursor()
        cursor.execute(inicial_clase_sql, [PERIODO_INICIAL, municipio_id])
        inicial_clase = dictfetchall(cursor)
        final_clase_sql = "SELECT year AS inversion__year,SUM(ejecutado) AS clase_final FROM core_proyecto JOIN core_inversion ON core_proyecto.inversion_id=core_inversion.id \
        JOIN lugar_clasificacionmunicano ON core_inversion.municipio_id=lugar_clasificacionmunicano.municipio_id AND \
        core_inversion.year=lugar_clasificacionmunicano.anio WHERE core_inversion.periodo=%s \
        AND lugar_clasificacionmunicano.clasificacion_id=(SELECT clasificacion_id FROM lugar_clasificacionmunicano WHERE municipio_id=%s AND lugar_clasificacionmunicano.anio=core_inversion.year) \
        GROUP BY year"
        cursor = connection.cursor()
        cursor.execute(final_clase_sql, [PERIODO_FINAL, municipio_id])
        final_clase = dictfetchall(cursor)

        # obtiene datos para municipio de la misma clase
        inicial_clase = Proyecto.objects.filter(inversion__periodo=PERIODO_INICIAL,\
                inversion__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, inversion__municipio__clase__anio=year).\
                values('inversion__year', 'inversion__periodo').order_by('inversion__periodo').annotate(clase_inicial=Sum('asignado'))
        final_clase = Proyecto.objects.filter(inversion__periodo=PERIODO_FINAL,\
                inversion__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, inversion__municipio__clase__anio=year).\
                values('inversion__year', 'inversion__periodo').order_by('inversion__periodo').annotate(clase_final=Sum('ejecutado'))

        for row in inicial:
            for row2 in inicial_clase:
                if row2['inversion__year'] == row['inversion__year']:
                    row['clase_inicial'] = row2['clase_inicial'] / mi_clase_anios_count[row['inversion__year']]
        for row in final:
            for row2 in final_clase:
                if row2['inversion__year'] == row['inversion__year']:
                    try:
                        row['clase_final'] = row2['clase_final'] / mi_clase_anios_count[row['inversion__year']]
                    except KeyError:
                        row['clase_final'] = 0
        for row in inicial:
            found = False
            for row2 in final:
                if row2['inversion__year'] == row['inversion__year']:
                    found = True
                    row['clase_final'] = row2['clase_final']
                    row['municipio_final'] = row2['municipio_final']
                if not found:
                    row['clase_final'] = 0
                    row['municipio_final'] = 0
        comparativo_anios = inicial

    else:
        municipio = ''
        source = Proyecto.objects.filter(inversion__year=year, inversion__periodo=periodo).values('catinversion__nombre').annotate(ejecutado=Sum(quesumar)).order_by('catinversion')
        source_clase = None
        source_ultimos = Proyecto.objects.filter(inversion__year__gt=year_list[-3]). \
            values('inversion__year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

        # tabla2, tabla3
        cat_inicial = Proyecto.objects.filter(inversion__periodo=PERIODO_INICIAL, inversion__year=year).values('catinversion__nombre').annotate(asignado=Sum('asignado')).order_by('catinversion')
        cat_actualizado = Proyecto.objects.filter(inversion__periodo=PERIODO_ACTUALIZADO, inversion__year=year).values('catinversion__nombre').annotate(ejecutado=Sum('ejecutado')).order_by('catinversion')
        cat_final = Proyecto.objects.filter(inversion__periodo=PERIODO_FINAL, inversion__year=year).values('catinversion__nombre').annotate(ejecutado=Sum('ejecutado')).order_by('catinversion')
        cat2 = glue(inicial=cat_inicial, final=cat_final, periodo=periodo, campo='catinversion__nombre')
        cat3 = glue(inicial=cat_inicial, final=cat_final, actualizado=cat_actualizado, periodo=periodo, campo='catinversion__nombre')

        # tabla4
        anual_inicial = Proyecto.objects.filter(inversion__periodo=PERIODO_INICIAL).values('inversion__year').annotate(asignado=Sum('asignado')).order_by('inversion__year')
        anual_actualizado = Proyecto.objects.filter(inversion__periodo=PERIODO_ACTUALIZADO).values('inversion__year').annotate(ejecutado=Sum('ejecutado')).order_by('inversion__year')
        anual_final = Proyecto.objects.filter(inversion__periodo=PERIODO_FINAL).values('inversion__year').annotate(ejecutado=Sum('ejecutado')).order_by('inversion__year')
        anual2 = glue(inicial=anual_inicial, final=anual_final, periodo=periodo, campo='inversion__year')
        anual3 = glue(inicial=anual_inicial, final=anual_final, actualizado=anual_actualizado, periodo=periodo, campo='inversion__year')

        # obtiene datos para grafico comparativo de tipo de inversions
        tipo_inicial= list(Proyecto.objects.filter(inversion__year=year, inversion__periodo=PERIODO_INICIAL).values('catinversion__nombre').order_by('catinversion__nombre').annotate(asignado=Sum('asignado')))
        tipo_final = list(Proyecto.objects.filter(inversion__year=year, inversion__periodo=PERIODO_FINAL).values('catinversion__nombre').order_by('catinversion__nombre').annotate(ejecutado=Sum('ejecutado')))
        tipo = glue(inicial=tipo_inicial, final=tipo_final, periodo=periodo, campo='catinversion__nombre')

        # obtiene datos para grafico comparativo de area
        area_inicial= list(Proyecto.objects.filter(inversion__year=year, inversion__periodo=PERIODO_INICIAL).values('areageografica').order_by('areageografica').annotate(asignado=Sum('asignado')))
        area_final = list(Proyecto.objects.filter(inversion__year=year, inversion__periodo=PERIODO_FINAL).values('areageografica').order_by('areageografica').annotate(ejecutado=Sum('ejecutado')))
        area = glue(area_inicial, area_final, periodo, 'areageografica')
        print area

        # obtiene datos para grafico comparativo de fuente
        fuente_inicial= list(InversionFuenteDetalle.objects.filter(inversionfuente__year=year, inversionfuente__periodo=PERIODO_INICIAL).values('fuente__nombre').order_by('fuente__nombre').annotate(asignado=Sum('asignado')))
        fuente_final = list(InversionFuenteDetalle.objects.filter(inversionfuente__year=year, inversionfuente__periodo=PERIODO_FINAL).values('fuente__nombre').order_by('fuente__nombre').annotate(ejecutado=Sum('ejecutado')))
        fuente = glue(fuente_inicial, fuente_final, periodo, 'fuente__nombre')
        fuente_actual = list(InversionFuenteDetalle.objects.filter(inversionfuente__year=year, inversionfuente__periodo=periodo).values('fuente__nombre').annotate(ejecutado=Sum(quesumar)))

    # conviert R en Rural, etc.
    for d in area:
        d.update((k, AREAGEOGRAFICA_VERBOSE[v]) for k, v in d.iteritems() if k == "areageografica")

    #
    # chartit!
    #
    if municipio:
        inversion_comparativo_anios = RawDataPool(
            series=
                [{'options': {'source': comparativo_anios },
                'terms':  ['inversion__year','inversion__periodo','municipio_inicial','municipio_final','clase_inicial','clase_final'],
                }],
            )
        inversion_comparativo_anios_column = Chart(
                datasource = inversion_comparativo_anios,
                series_options =
                [{'options':{
                    'type': 'column',
                    'stacking': False},
                    'terms':{
                    'inversion__year': ['municipio_inicial', 'clase_inicial', 'municipio_final', 'clase_final'],
                    },
                    }],
                chart_options =
                {'title': { 'text': 'Inversiones %s' % (municipio,)}},
                )
    inversion_fuente = RawDataPool(
        series=
            [{'options': {'source': fuente },
            'terms':  ['fuente__nombre','ejecutado','asignado'],
            }],
        )
    inversion_fuente_column = Chart(
            datasource = inversion_fuente,
            series_options =
            [{'options':{
                'type': 'column',
                'stacking': False},
                'terms':{
                'fuente__nombre': ['ejecutado', 'asignado'],
                },
                }],
            chart_options =
            {
                'title': { 'text': 'Inversions por fuente origen %s %s' % (year, municipio,)},
                'data': { 'table': 'datatable'},
            },
    )
    inversion_fuente_actual = RawDataPool(
        series=
            [{'options': {'source': fuente_actual },
            'terms':  ['fuente__nombre','ejecutado'],
            }],
        )
    inversion_fuente_pie = Chart(
            datasource = inversion_fuente_actual,
            series_options =
            [{'options':{
                'type': 'pie',
                'stacking': False},
                'terms':{
                'fuente__nombre': ['ejecutado'],
                },
                }],
            chart_options =
              {'title': {
                  'text': 'Inversions por fuente origen %s %s' % (year, municipio,)},
                  'options3d': { 'enabled': 'true',  'alpha': '45', 'beta': '0' },
                  'plotOptions': { 'pie': { 'dataLabels': { 'enabled': False }, 'showInLegend': True, 'depth': 35}},
                  'tooltip': { 'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>' },
              }
    )
    inversion_area = RawDataPool(
        series=
            [{'options': {'source': area },
            'terms':  ['areageografica','ejecutado','asignado'],
            }],
        )
    inversion_area_column = Chart(
            datasource = inversion_area,
            series_options =
            [{'options':{
                'type': 'column',
                'stacking': False},
                'terms':{
                'areageografica': ['ejecutado', 'asignado'],
                },
                }],
            chart_options =
            {
                'title': { 'text': 'Inversions por area origen %s %s' % (year, municipio,)},
                'data': { 'table': 'datatable'},
            },
    )
    inversion_tipo = RawDataPool(
        series=
            [{'options': {'source': tipo },
            'terms':  ['catinversion__nombre','ejecutado','asignado'],
            }],
        )
    inversion_tipo_column = Chart(
            datasource = inversion_tipo,
            series_options =
            [{'options':{
                'type': 'column',
                'stacking': False},
                'terms':{
                'catinversion__nombre': ['ejecutado', 'asignado'],
                },
                }],
            chart_options =
            {
                'title': { 'text': 'Inversions por tipo origen %s %s' % (year, municipio,)},
                'data': { 'table': 'datatable'},
            },
    )
    data_ultimos = DataPool(
           series=
            [{'options': {
                'source': source_ultimos,
                'categories': 'inversion__year',
                },
              'terms': ['inversion__year', 'ejecutado', 'asignado',]
            }],
    )
    ultimos = Chart(
            datasource = data_ultimos,
            series_options =
              [{'options':{
                  'type': 'bar',
                  'stacking': False},
                'terms': {'inversion__year': ['asignado', 'ejecutado']}
                }],
            chart_options =
              {'title': {'text': u'Inversión por últimos años %s' % (municipio, )}},
    )
    oimdata = DataPool(
           series=
            [{'options': {'source': source },
              'terms': [
                'catinversion__nombre',
                'ejecutado',
                ]}
             ])

    ejecutado = Chart(
            datasource = oimdata,
            series_options =
              [{'options':{
                  'type': 'pie',
                  },
                'terms':{
                  'catinversion__nombre': [
                    'ejecutado']
                  }}],
            chart_options =
              {'title': {
                  'text': 'Inversion %s %s %s' % (quesumar, municipio, year,)},
                  'options3d': { 'enabled': 'true',  'alpha': '45', 'beta': '0' },
                  'plotOptions': { 'pie': { 'dataLabels': { 'enabled': False }, 'showInLegend': True, 'depth': 35}},
                  'tooltip': { 'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>' },
              })

    # tabla: get total and percent
    source_list = list(source)
    total = source.aggregate(total=Sum('ejecutado'))['total']
    for row in source:
        row['percent'] = round(row['ejecutado'] / total * 100, 0)

    if source_clase:
        total_clase = source_clase.aggregate(total=Sum('clase'))['total']
        for row in source_clase:
            row['clase_percent'] = round(row['clase'] / total_clase * 100, 0)
        for row in source_list:
            for row2 in source_clase:
                if row2['catinversion__nombre'] == row['catinversion__nombre']:
                    row['clase'] = row2['clase']
                    row['clase_percent'] = row2['clase_percent']
    #print source_list

    # tabla: get inversions por año
    porano_table = {}
    ys = source_ultimos.order_by('catinversion__nombre').values('catinversion__nombre').distinct()
    for y in ys:
        label = y['catinversion__nombre']
        porano_table[label] = {}
        for ayear in year_list:
            value = source_ultimos.filter(inversion__year=ayear, catinversion__nombre=label).aggregate(total=Sum('asignado'))['total']
            porano_table[label][ayear] = value if value else ''
        if municipio and year:
            periodo = PERIODO_FINAL
            quesumar = 'ejecutado'
            value = Proyecto.objects.filter(inversion__year=year, inversion__periodo=periodo, tipoproyecto__nombre=label, \
                    inversion__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, inversion__municipio__clase__anio=year).\
                    aggregate(total=Avg(quesumar))['total']
            porano_table[label]['extra'] = value if value else '...'

    mi_clase = None

    if portada:
        charts =  (ejecutado, )
    elif municipio:
        charts =  (inversion_tipo_column, inversion_area_column, inversion_fuente_column, inversion_fuente_pie, inversion_comparativo_anios_column, ejecutado, ultimos )
    else:
        charts =  (inversion_tipo_column, inversion_area_column, inversion_fuente_column, inversion_fuente_pie, ejecutado, ultimos )

    return {'charts': charts, \
            'clasificacion': mi_clase, 'anio': year, 'porano': porano_table, 'totales': source_list, 'cat': cat3, 'anuales': anual3,\
            'year_list': year_list, 'municipio_list': municipio_list, 'municipio': municipio}
