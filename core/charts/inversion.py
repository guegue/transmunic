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
            inversion__anio__gt=list(year_list)[-3]). \
            values('inversion__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
    else:
        municipio = ''
        source = Proyecto.objects.filter(inversion__periodo=PERIODO_INICIAL). \
            values('inversion__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_ultimos = Proyecto.objects.filter(inversion__periodo=PERIODO_INICIAL, inversion__anio__gt=list(year_list)[-3]). \
            values('inversion__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

    data_ultimos = DataPool(
           series=
            [{'options': {
                'source': source_ultimos,
                'categories': 'inversion__anio',
                },
              'terms': ['inversion__anio', 'ejecutado', 'asignado',]
            }],
    )
    chart_ultimos = Chart(
            datasource = data_ultimos,
            series_options =
              [{'options':{
                  'type': 'bar',
                  'stacking': False},
                'terms': {'inversion__anio': ['asignado', 'ejecutado']}
                }],
            chart_options =
              {'title': {'text': u'Inversión por últimos años %s' % (municipio, )}},
            #x_sortf_mapf_mts = (None, lambda i:  i.strftime('%Y'), False)
    )
    data = DataPool(
           series=
            [{'options': {
                'source': source,
                'categories': 'inversion__anio',
                },
              'terms': ['inversion__anio', 'ejecutado', 'asignado',]
            }],
    )
    chart = Chart(
            datasource = data,
            series_options =
              [{'options':{
                  'type': 'bar',
                  'stacking': False},
                'terms': {'inversion__anio': ['asignado', 'ejecutado']}
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
        source_ultimos = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__anio__gt=year_list[-3]). \
            values('inversion__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

        # tabla2, tabla3
        cat_inicial = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__periodo=PERIODO_INICIAL, inversion__anio=year).values('catinversion__nombre').annotate(asignado=Sum('asignado')).order_by('catinversion')
        cat_actualizado = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__periodo=PERIODO_ACTUALIZADO, inversion__anio=year).values('catinversion__nombre').annotate(ejecutado=Sum('ejecutado')).order_by('catinversion')
        cat_final = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__periodo=PERIODO_FINAL, inversion__anio=year).values('catinversion__nombre').annotate(ejecutado=Sum('ejecutado')).order_by('catinversion')
        cat2 = glue(inicial=cat_inicial, final=cat_final, periodo=periodo, campo='catinversion__nombre')
        cat3 = glue(inicial=cat_inicial, final=cat_final, actualizado=cat_actualizado, periodo=periodo, campo='catinversion__nombre')

        # tabla4
        anual_inicial = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__periodo=PERIODO_INICIAL).values('inversion__anio').annotate(asignado=Sum('asignado')).order_by('inversion__anio')
        anual_actualizado = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__periodo=PERIODO_ACTUALIZADO).values('inversion__anio').annotate(ejecutado=Sum('ejecutado')).order_by('inversion__anio')
        anual_final = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__periodo=PERIODO_FINAL).values('inversion__anio').annotate(ejecutado=Sum('ejecutado')).order_by('inversion__anio')
        anual2 = glue(inicial=anual_inicial, final=anual_final, periodo=periodo, campo='inversion__anio')
        anual3 = glue(inicial=anual_inicial, final=anual_final, actualizado=anual_actualizado, periodo=periodo, campo='inversion__anio')

        # obtiene datos percapita
        percapita_inicial_sql = "SELECT year AS inversion__anio,SUM(asignado)/poblacion AS asignado FROM core_proyecto JOIN core_inversion ON core_proyecto.inversion_id=core_inversion.id \
        JOIN lugar_poblacion ON core_inversion.municipio_id=lugar_poblacion.municipio_id AND core_inversion.year=lugar_poblacion.anio WHERE core_inversion.municipio_id=%s AND core_inversion.periodo=%s GROUP BY year,poblacion"
        cursor = connection.cursor()
        cursor.execute(percapita_inicial_sql, [municipio_id, PERIODO_INICIAL])
        percapita_inicial = dictfetchall(cursor)
        percapita_actualizado_sql = "SELECT year AS inversion__anio,SUM(ejecutado)/poblacion AS ejecutado FROM core_proyecto JOIN core_inversion ON core_proyecto.inversion_id=core_inversion.id \
        JOIN lugar_poblacion ON core_inversion.municipio_id=lugar_poblacion.municipio_id AND core_inversion.year=lugar_poblacion.anio WHERE core_inversion.municipio_id=%s AND core_inversion.periodo=%s GROUP BY year,poblacion"
        cursor = connection.cursor()
        cursor.execute(percapita_actualizado_sql, [municipio_id, PERIODO_ACTUALIZADO])
        percapita_actualizado = dictfetchall(cursor)
        percapita_final_sql = "SELECT year AS inversion__anio,SUM(ejecutado)/poblacion AS ejecutado FROM core_proyecto JOIN core_inversion ON core_proyecto.inversion_id=core_inversion.id \
        JOIN lugar_poblacion ON core_inversion.municipio_id=lugar_poblacion.municipio_id AND core_inversion.year=lugar_poblacion.anio WHERE core_inversion.municipio_id=%s AND core_inversion.periodo=%s GROUP BY year,poblacion"
        cursor = connection.cursor()
        cursor.execute(percapita_final_sql, [municipio_id, PERIODO_FINAL])
        percapita_final = dictfetchall(cursor)
        percapita3 = glue(inicial=percapita_inicial, final=percapita_final, actualizado=percapita_actualizado, periodo=periodo, campo='inversion__anio')
        print percapita3

        # obtiene clase y contador (otros en misma clase) para este año
        mi_clase = ClasificacionMunicAno.objects.get(municipio__slug=municipio, anio=year)
        mi_clase_count = ClasificacionMunicAno.objects.filter(clasificacion__clasificacion=mi_clase.clasificacion, anio=year).count()
        # obtiene clase y contador (otros en misma clase) para todos los años
        mi_clase_anios = list(ClasificacionMunicAno.objects.filter(municipio__slug=municipio).values('anio', 'clasificacion__clasificacion').annotate())
        mi_clase_anios_count = {}
        for aclase in mi_clase_anios:
            mi_clase_anios_count[aclase['anio']] = ClasificacionMunicAno.objects.filter(clasificacion__clasificacion=aclase['clasificacion__clasificacion'], anio=aclase['anio']).count()

        # source base
        source = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__anio=year, inversion__periodo=periodo).values('catinversion__nombre').annotate(ejecutado=Sum(quesumar)).order_by('catinversion')
        source_clase = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__anio=year, inversion__periodo=periodo,\
                inversion__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, inversion__municipio__clase__anio=year).\
                values('catinversion__nombre').annotate(clase=Sum(quesumar))


        # obtiene datos para grafico comparativo de tipo de inversions
        tipo_inicial= list(Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__anio=year, inversion__periodo=PERIODO_INICIAL).values('catinversion__nombre').annotate(asignado=Sum('asignado')))
        tipo_actualizado = list(Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__anio=year, inversion__periodo=PERIODO_ACTUALIZADO).values('catinversion__nombre').annotate(ejecutado=Sum('ejecutado')))
        tipo_final = list(Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__anio=year, inversion__periodo=PERIODO_FINAL).values('catinversion__nombre').annotate(ejecutado=Sum('ejecutado')))
        tipo = glue(inicial=tipo_inicial, final=tipo_final, periodo=periodo, campo='catinversion__nombre', actualizado=tipo_actualizado)

        # obtiene datos para grafico comparativo por area
        area_inicial= list(Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__anio=year, inversion__periodo=PERIODO_INICIAL).values('areageografica').annotate(asignado=Sum('asignado')))
        area_final = list(Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__anio=year, inversion__periodo=PERIODO_FINAL).values('areageografica').annotate(ejecutado=Sum('ejecutado')))
        area = glue(area_inicial, area_final, periodo, 'areageografica')

        # obtiene datos para grafico comparativo por fuente
        fuente_inicial = list(InversionFuenteDetalle.objects.filter(inversionfuente__municipio__slug=municipio, inversionfuente__anio=year, inversionfuente__periodo=PERIODO_INICIAL).values('fuente__nombre').annotate(asignado=Sum('asignado')))
        fuente_final = list(InversionFuenteDetalle.objects.filter(inversionfuente__municipio__slug=municipio, inversionfuente__anio=year, inversionfuente__periodo=PERIODO_FINAL).values('fuente__nombre').annotate(ejecutado=Sum('ejecutado')))
        fuente = glue(fuente_inicial, fuente_final, periodo, 'fuente__nombre')
        fuente_actual = list(InversionFuenteDetalle.objects.filter(inversionfuente__municipio__slug=municipio, inversionfuente__anio=year, inversionfuente__periodo=periodo).values('fuente__nombre').annotate(ejecutado=Sum(quesumar)))

    else:
        municipio = ''
        source = Proyecto.objects.filter(inversion__anio=year, inversion__periodo=periodo).values('catinversion__nombre').annotate(ejecutado=Sum(quesumar)).order_by('catinversion')
        source_clase = None
        source_ultimos = Proyecto.objects.filter(inversion__anio__gt=year_list[-3]). \
            values('inversion__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

        # tabla2, tabla3
        cat_inicial = Proyecto.objects.filter(inversion__periodo=PERIODO_INICIAL, inversion__anio=year).values('catinversion__nombre').annotate(asignado=Sum('asignado')).order_by('catinversion')
        cat_actualizado = Proyecto.objects.filter(inversion__periodo=PERIODO_ACTUALIZADO, inversion__anio=year).values('catinversion__nombre').annotate(ejecutado=Sum('ejecutado')).order_by('catinversion')
        cat_final = Proyecto.objects.filter(inversion__periodo=PERIODO_FINAL, inversion__anio=year).values('catinversion__nombre').annotate(ejecutado=Sum('ejecutado')).order_by('catinversion')
        cat2 = glue(inicial=cat_inicial, final=cat_final, periodo=periodo, campo='catinversion__nombre')
        cat3 = glue(inicial=cat_inicial, final=cat_final, actualizado=cat_actualizado, periodo=periodo, campo='catinversion__nombre')

        # tabla4
        anual_inicial = Proyecto.objects.filter(inversion__periodo=PERIODO_INICIAL).values('inversion__anio').annotate(asignado=Sum('asignado')).order_by('inversion__anio')
        anual_actualizado = Proyecto.objects.filter(inversion__periodo=PERIODO_ACTUALIZADO).values('inversion__anio').annotate(ejecutado=Sum('ejecutado')).order_by('inversion__anio')
        anual_final = Proyecto.objects.filter(inversion__periodo=PERIODO_FINAL).values('inversion__anio').annotate(ejecutado=Sum('ejecutado')).order_by('inversion__anio')
        anual2 = glue(inicial=anual_inicial, final=anual_final, periodo=periodo, campo='inversion__anio')
        anual3 = glue(inicial=anual_inicial, final=anual_final, actualizado=anual_actualizado, periodo=periodo, campo='inversion__anio')

        # obtiene datos para grafico comparativo de tipo de inversions
        tipo_inicial= list(Proyecto.objects.filter(inversion__anio=year, inversion__periodo=PERIODO_INICIAL).values('catinversion__nombre').order_by('catinversion__nombre').annotate(asignado=Sum('asignado')))
        tipo_actualizado = list(Proyecto.objects.filter(inversion__anio=year, inversion__periodo=PERIODO_ACTUALIZADO).values('catinversion__nombre').annotate(ejecutado=Sum('ejecutado')))
        tipo_final = list(Proyecto.objects.filter(inversion__anio=year, inversion__periodo=PERIODO_FINAL).values('catinversion__nombre').order_by('catinversion__nombre').annotate(ejecutado=Sum('ejecutado')))
        tipo = glue(inicial=tipo_inicial, final=tipo_final, periodo=periodo, campo='catinversion__nombre', actualizado=tipo_actualizado)

        # obtiene datos para grafico comparativo de area
        area_inicial= list(Proyecto.objects.filter(inversion__anio=year, inversion__periodo=PERIODO_INICIAL).values('areageografica').order_by('areageografica').annotate(asignado=Sum('asignado')))
        area_final = list(Proyecto.objects.filter(inversion__anio=year, inversion__periodo=PERIODO_FINAL).values('areageografica').order_by('areageografica').annotate(ejecutado=Sum('ejecutado')))
        area = glue(area_inicial, area_final, periodo, 'areageografica')

        # obtiene datos para grafico comparativo de fuente
        fuente_inicial= list(InversionFuenteDetalle.objects.filter(inversionfuente__anio=year, inversionfuente__periodo=PERIODO_INICIAL).values('fuente__nombre').order_by('fuente__nombre').annotate(asignado=Sum('asignado')))
        fuente_final = list(InversionFuenteDetalle.objects.filter(inversionfuente__anio=year, inversionfuente__periodo=PERIODO_FINAL).values('fuente__nombre').order_by('fuente__nombre').annotate(ejecutado=Sum('ejecutado')))
        fuente = glue(fuente_inicial, fuente_final, periodo, 'fuente__nombre')
        fuente_actual = list(InversionFuenteDetalle.objects.filter(inversionfuente__anio=year, inversionfuente__periodo=periodo).values('fuente__nombre').annotate(ejecutado=Sum(quesumar)))

    # conviert R en Rural, etc.
    for d in area:
        d.update((k, AREAGEOGRAFICA_VERBOSE[v]) for k, v in d.iteritems() if k == "areageografica")

    #
    # chartit!
    #
    if municipio:
        inversion_percapita_anios = RawDataPool(
            series=
                [{'options': {'source': percapita3 },
                'terms':  ['inversion__anio','actualizado','asignado','ejecutado',],
                }],
            )
        inversion_percapita_anios_column = Chart(
                datasource = inversion_percapita_anios,
                series_options =
                [{'options':{
                    'type': 'column',
                    'stacking': False},
                    'terms':{
                    'inversion__anio': ['asignado', 'ejecutado', 'actualizado'],
                    },
                    }],
                chart_options =
                {'title': { 'text': u'Seguimiento de las Inversiones percápita %s' % (municipio,)}},
                )
        inversion_comparativo_anios = RawDataPool(
            series=
                [{'options': {'source': anual3 },
                'terms':  ['inversion__anio','actualizado','asignado','ejecutado',],
                }],
            )
        inversion_comparativo_anios_column = Chart(
                datasource = inversion_comparativo_anios,
                series_options =
                [{'options':{
                    'type': 'column',
                    'stacking': False},
                    'terms':{
                    'inversion__anio': ['asignado', 'ejecutado', 'actualizado'],
                    },
                    }],
                chart_options =
                {'title': { 'text': 'Seguimiento de las Inversiones %s' % (municipio,)}},
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
                  'plotOptions': { 'pie': { 'dataLabels': { 'enabled': True, 'format': '{point.percentage:.1f} %' }, 'showInLegend': True, 'depth': 35}},
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
            'terms':  ['catinversion__nombre','ejecutado','asignado','actualizado'],
            }],
        )
    inversion_tipo_column = Chart(
            datasource = inversion_tipo,
            series_options =
            [{'options':{
                'type': 'column',
                'stacking': False},
                'terms':{
                'catinversion__nombre': ['ejecutado', 'asignado','actualizado'],
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
                'categories': 'inversion__anio',
                },
              'terms': ['inversion__anio', 'ejecutado', 'asignado',]
            }],
    )
    ultimos = Chart(
            datasource = data_ultimos,
            series_options =
              [{'options':{
                  'type': 'bar',
                  'stacking': False},
                'terms': {'inversion__anio': ['asignado', 'ejecutado']}
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
                  'plotOptions': { 'pie': { 'dataLabels': { 'enabled': True, 'format': '{point.percentage:.1f} %' }, 'showInLegend': True, 'depth': 35}},
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
            value = source_ultimos.filter(inversion__anio=ayear, catinversion__nombre=label).aggregate(total=Sum('asignado'))['total']
            porano_table[label][ayear] = value if value else ''
        if municipio and year:
            periodo = PERIODO_FINAL
            quesumar = 'ejecutado'
            value = Proyecto.objects.filter(inversion__anio=year, inversion__periodo=periodo, tipoproyecto__nombre=label, \
                    inversion__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, inversion__municipio__clase__anio=year).\
                    aggregate(total=Avg(quesumar))['total']
            porano_table[label]['extra'] = value if value else '...'

    mi_clase = None

    if portada:
        charts =  (ejecutado, )
    elif municipio:
        charts =  (inversion_tipo_column, inversion_area_column, inversion_fuente_column, inversion_fuente_pie, inversion_comparativo_anios_column, inversion_percapita_anios_column, ejecutado, ultimos )
    else:
        charts =  (inversion_tipo_column, inversion_area_column, inversion_fuente_column, inversion_fuente_pie, ejecutado, ultimos )

    return {'charts': charts, \
            'clasificacion': mi_clase, 'anio': year, 'porano': porano_table, 'totales': source_list, 'cat': cat3, 'anuales': anual3,\
            'year_list': year_list, 'municipio_list': municipio_list, 'municipio': municipio}
