# -*- coding: utf-8 -*-

from operator import itemgetter

from django.db import connection
from django.db.models import Sum, Avg

from chartit import DataPool, Chart, RawDataPool

from core.models import (Anio, Proyecto, Inversion, Municipio,
                         InversionFuenteDetalle, PERIODO_INICIAL,
                         PERIODO_ACTUALIZADO, PERIODO_FINAL,
                         AREAGEOGRAFICA_VERBOSE)
from core.tools import (getYears, getPeriods, dictfetchall, glue,
                        superglue, percentage, xnumber, graphChart)
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


def inversion_chart(municipio=None):
    municipio_list = Municipio.objects.all()
    periodo_list = getPeriods(Inversion)
    year_list = getYears(Inversion)

    if municipio:
        source = Proyecto.objects.filter(inversion__periodo=PERIODO_INICIAL, inversion__municipio__slug=municipio). \
            values('inversion__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
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
# Inversion charts /core/inversion-categoria FIXME: yep, mal nombre...
#
##############################################################################
def inversion_categoria_chart(municipio=None, year=None, portada=False):
    municipio_list = Municipio.objects.all()
    year_list = getYears(Inversion)
    periodo_list = getPeriods(Inversion)
    if not year:
        year = year_list[-1]

    periodo = Anio.objects.get(anio=year).periodo
    datacol = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'

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

        source_ultimos = Proyecto.objects.filter(
            inversion__municipio__slug=municipio,
            inversion__anio__gt=year_list[-6])\
            .values('inversion__anio')\
            .annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

        # tabla2, tabla3
        cat_inicial = Proyecto.objects.filter(
            inversion__municipio__slug=municipio,
            inversion__periodo=PERIODO_INICIAL,
            inversion__anio=year)\
            .values(
                'catinversion__nombre', 'catinversion__id',
                'catinversion__shortname', 'catinversion__color',
                'catinversion__slug')\
            .annotate(inicial_asignado=Sum('asignado'))\
            .order_by('catinversion')

        cat_actualizado = Proyecto.objects.filter(
            inversion__municipio__slug=municipio,
            inversion__periodo=PERIODO_ACTUALIZADO,
            inversion__anio=year)\
            .values(
                'catinversion__nombre', 'catinversion__id',
                'catinversion__shortname', 'catinversion__color',
                'catinversion__slug')\
            .annotate(
                actualizado_asignado=Sum('asignado'),
                actualizado_ejecutado=Sum('ejecutado'))\
            .order_by('catinversion')

        cat_final = Proyecto.objects.filter(
            inversion__municipio__slug=municipio,
            inversion__periodo=PERIODO_FINAL,
            inversion__anio=year)\
            .values(
                'catinversion__nombre', 'catinversion__id',
                'catinversion__shortname', 'catinversion__color',
                'catinversion__slug')\
            .annotate(
                final_ejecutado=Sum('ejecutado'),
                final_asignado=Sum('asignado'))\
            .order_by('catinversion')

        cat_periodo = Proyecto.objects.filter(
            inversion__municipio__slug=municipio,
            inversion__periodo=periodo,
            inversion__anio=year)\
            .values(
                'catinversion__nombre', 'catinversion__id',
                'catinversion__shortname', 'catinversion__color',
                'catinversion__slug')\
            .annotate(
                ejecutado=Sum('ejecutado'),
                asignado=Sum('asignado'))\
            .order_by('catinversion')

        cat2 = superglue(
            data=(cat_inicial, cat_final),
            key='catinversion__nombre')
        cat3 = superglue(
            data=(cat_inicial, cat_final, cat_actualizado, cat_periodo),
            key='catinversion__nombre')

        # tabla4
        anual_inicial = Proyecto.objects.filter(
            inversion__municipio__slug=municipio,
            inversion__periodo=PERIODO_INICIAL)\
            .values('inversion__anio')\
            .annotate(asignado=Sum('asignado'))\
            .order_by('inversion__anio')

        anual_actualizado = Proyecto.objects.filter(
            inversion__municipio__slug=municipio,
            inversion__periodo=PERIODO_ACTUALIZADO)\
            .values('inversion__anio')\
            .annotate(asignado=Sum('asignado'))\
            .order_by('inversion__anio')

        anual_final = Proyecto.objects.filter(
            inversion__municipio__slug=municipio,
            inversion__periodo=PERIODO_FINAL)\
            .values('inversion__anio')\
            .annotate(ejecutado=Sum('ejecutado'))\
            .order_by('inversion__anio')

        anual2 = glue(
            inicial=anual_inicial, final=anual_final,
            key='inversion__anio')
        anual3 = glue(
            inicial=anual_inicial, final=anual_final,
            actualizado=anual_actualizado, key='inversion__anio')

        # obtiene datos percapita
        percapita_inicial_sql = """SELECT core_inversion.anio
            AS inversion__anio,
            SUM(asignado)/poblacion AS asignado
            FROM core_proyecto
            JOIN core_inversion
            ON core_proyecto.inversion_id=core_inversion.id
            JOIN lugar_poblacion
            ON core_inversion.municipio_id=lugar_poblacion.municipio_id
            AND core_inversion.anio=lugar_poblacion.anio
            WHERE core_inversion.municipio_id=%s
            AND core_inversion.periodo=%s
            GROUP BY core_inversion.anio,poblacion"""
        cursor = connection.cursor()
        cursor.execute(percapita_inicial_sql, [municipio_id, PERIODO_INICIAL])
        percapita_inicial = dictfetchall(cursor)

        percapita_actualizado_sql = """SELECT core_inversion.anio
            AS inversion__anio,
            SUM(asignado)/poblacion AS asignado
            FROM core_proyecto
            JOIN core_inversion
            ON core_proyecto.inversion_id=core_inversion.id
            JOIN lugar_poblacion
            ON core_inversion.municipio_id=lugar_poblacion.municipio_id
            AND core_inversion.anio=lugar_poblacion.anio
            WHERE core_inversion.municipio_id=%s
            AND core_inversion.periodo=%s
            GROUP BY core_inversion.anio, poblacion"""
        cursor = connection.cursor()
        cursor.execute(percapita_actualizado_sql, [municipio_id, PERIODO_ACTUALIZADO])
        percapita_actualizado = dictfetchall(cursor)

        percapita_final_sql = """SELECT core_inversion.anio AS inversion__anio,
            SUM(ejecutado)/poblacion AS ejecutado
            FROM core_proyecto
            JOIN core_inversion
            ON core_proyecto.inversion_id=core_inversion.id
            JOIN lugar_poblacion
            ON core_inversion.municipio_id=lugar_poblacion.municipio_id
            AND core_inversion.anio=lugar_poblacion.anio
            WHERE core_inversion.municipio_id=%s
            AND core_inversion.periodo=%s
            GROUP BY core_inversion.anio,poblacion"""
        cursor = connection.cursor()
        cursor.execute(percapita_final_sql, [municipio_id, PERIODO_FINAL])
        percapita_final = dictfetchall(cursor)

        percapita3 = glue(
            inicial=percapita_inicial, final=percapita_final,
            actualizado=percapita_actualizado, key='inversion__anio')

        # obtiene clase y contador (otros en misma clase) para este año
        mi_clase = ClasificacionMunicAno.objects.get(
            municipio__slug=municipio, anio=year)
        mi_clase_count = ClasificacionMunicAno.objects.filter(
            clasificacion__clasificacion=mi_clase.clasificacion, anio=year)\
            .count()
        # obtiene clase y contador (otros en misma clase) para todos los años
        mi_clase_anios = list(
            ClasificacionMunicAno.objects.filter(municipio__slug=municipio)
            .values('anio', 'clasificacion__clasificacion').annotate())
        mi_clase_anios_count = {}

        for aclase in mi_clase_anios:
            mi_clase_anios_count[aclase['anio']] = \
                ClasificacionMunicAno.objects.filter(
                    clasificacion__clasificacion=aclase[
                        'clasificacion__clasificacion'
                        ],
                    anio=aclase['anio']).count()

        # obtiene datos de municipios de la misma clase
        municipios_inicial = Proyecto.objects.filter(
            inversion__anio=year, inversion__periodo=PERIODO_INICIAL,
            inversion__municipio__clase__anio=year,
            inversion__municipio__clasificaciones__clasificacion=mi_clase.clasificacion)\
            .values(
                'inversion__municipio__nombre', 'inversion__municipio__slug')\
            .order_by('inversion__municipio__nombre')\
            .annotate(asignado=Sum('asignado'))

        municipios_actualizado = Proyecto.objects.filter(
            inversion__anio=year, inversion__periodo=PERIODO_ACTUALIZADO,
            inversion__municipio__clase__anio=year,
            inversion__municipio__clasificaciones__clasificacion=mi_clase.clasificacion)\
            .values(
                'inversion__municipio__nombre', 'inversion__municipio__slug')\
            .order_by('inversion__municipio__nombre')\
            .annotate(asignado=Sum('asignado'))

        municipios_final = Proyecto.objects.filter(
            inversion__anio=year, inversion__periodo=periodo,
            inversion__municipio__clase__anio=year,
            inversion__municipio__clasificaciones__clasificacion=mi_clase.clasificacion)\
            .values(
                'inversion__municipio__nombre', 'inversion__municipio__slug')\
            .order_by('inversion__municipio__nombre')\
            .annotate(ejecutado=Sum('ejecutado'))

        otros = glue(
            municipios_inicial, municipios_final,
            'inversion__municipio__nombre', actualizado=municipios_actualizado)
        # inserta porcentages de total de gastos
        for row in otros:
            try:
                total_poblacion = Poblacion.objects.get(
                    anio=year,
                    municipio__slug=row['inversion__municipio__slug'])\
                    .poblacion
            except:
                total_poblacion = 0

            row['poblacion'] = total_poblacion
            row['ejecutado_percent'] = round(row['ejecutado'] / total_poblacion, 1) if row['ejecutado'] and total_poblacion > 0 else 0
            row['asignado_percent'] = round(row['asignado'] / total_poblacion, 1) if row['asignado'] and total_poblacion > 0 else 0

        otros = sorted(otros, key=itemgetter('ejecutado_percent'), reverse=True)

        # source base
        source = Proyecto.objects.filter(
            inversion__municipio__slug=municipio,
            inversion__anio=year)\
            .values('catinversion__nombre')\
            .annotate(ejecutado=Sum(quesumar))\
            .order_by('catinversion__nombre')

        tipos_inicial = Proyecto.objects.filter(
            inversion__municipio__slug=municipio,
            inversion__anio=year, inversion__periodo=PERIODO_INICIAL)\
            .values('catinversion__nombre')\
            .annotate(asignado=Sum('asignado')).order_by('catinversion__nombre')

        tipos_final = Proyecto.objects.filter(\
            inversion__municipio__slug=municipio, inversion__anio=year,
            inversion__periodo=periodo)\
            .values('catinversion__nombre')\
            .annotate(ejecutado=Sum('ejecutado'))\
            .order_by('catinversion__nombre')

        sources = glue(tipos_inicial, tipos_final, 'catinversion__nombre')

        source_clase = Proyecto.objects.filter(
            inversion__municipio__slug=municipio, inversion__anio=year,
            inversion__periodo=periodo,
            inversion__municipio__clasificaciones__clasificacion=mi_clase.clasificacion,
            inversion__municipio__clase__anio=year)\
            .values('catinversion__nombre')\
            .annotate(clase=Sum(quesumar))

        source_inicial = Proyecto.objects.filter(inversion__periodo=PERIODO_INICIAL, \
            inversion__municipio__slug=municipio).\
            values('inversion__anio').\
            annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by()
        source_final = Proyecto.objects.filter(inversion__periodo=periodo, \
            inversion__municipio__slug=municipio).\
            values('inversion__anio').\
            annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by()
        # obtiene valores para este año de las listas
        try:
            asignado = (item for item in source_inicial
                        if item["inversion__anio"] == int(year)).next()['asignado']
        except StopIteration:
            asignado = 0
        try:
            ejecutado = (item for item in source_final
                         if item["inversion__anio"] == int(year)).next()['ejecutado']
        except StopIteration:
            ejecutado = 0

        # obtiene datos para grafico comparativo de tipo de inversions
        tipo_inicial= list(Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__anio=year, inversion__periodo=PERIODO_INICIAL).values('catinversion__nombre').annotate(asignado=Sum('asignado')))
        tipo_actualizado = list(Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__anio=year, inversion__periodo=PERIODO_ACTUALIZADO).values('catinversion__nombre').annotate(asignado=Sum('asignado')))
        tipo_final = list(Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__anio=year, inversion__periodo=PERIODO_FINAL).values('catinversion__nombre').annotate(ejecutado=Sum('ejecutado')))
        tipo = glue(inicial=tipo_inicial, final=tipo_final, key='catinversion__nombre', actualizado=tipo_actualizado)

        # obtiene datos para grafico comparativo por area
        area_inicial= list(Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__anio=year, inversion__periodo=PERIODO_INICIAL).values('areageografica').annotate(asignado=Sum('asignado')))
        area_final = list(Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__anio=year, inversion__periodo=PERIODO_FINAL).values('areageografica').annotate(ejecutado=Sum('ejecutado')))
        area = glue(area_inicial, area_final, 'areageografica')

        # obtiene datos para grafico comparativo por fuente
        fuente_inicial = list(InversionFuenteDetalle.objects.filter(inversionfuente__municipio__slug=municipio, inversionfuente__anio=year, inversionfuente__periodo=PERIODO_INICIAL).values('fuente__nombre').order_by('fuente__nombre').annotate(asignado=Sum('asignado')))
        fuente_final = list(InversionFuenteDetalle.objects.filter(inversionfuente__municipio__slug=municipio, inversionfuente__anio=year, inversionfuente__periodo=PERIODO_FINAL).values('fuente__nombre').order_by('fuente__nombre').annotate(ejecutado=Sum('ejecutado')))
        fuente = glue(fuente_inicial, fuente_final, 'fuente__nombre')
        fuente_actual = list(InversionFuenteDetalle.objects.filter(inversionfuente__municipio__slug=municipio, inversionfuente__anio=year, inversionfuente__periodo=periodo).values('fuente__nombre').order_by('fuente__nombre').annotate(ejecutado=Sum(quesumar)))

    else:
        #
        # no municipio
        #
        otros = None
        mi_clase = None
        municipio_row = ''
        municipio = ''

        source = Proyecto.objects.filter(
            inversion__anio=year, inversion__periodo=periodo)\
            .values('catinversion__nombre')\
            .order_by('catinversion__nombre')\
            .annotate(ejecutado=Sum(quesumar))
        tipos_inicial = Proyecto.objects.filter(
            inversion__anio=year, inversion__periodo=PERIODO_INICIAL)\
            .values('catinversion__nombre')\
            .annotate(asignado=Sum('asignado'))\
            .order_by('catinversion__nombre')
        tipos_final = Proyecto.objects.filter(
            inversion__anio=year, inversion__periodo=periodo)\
            .values('catinversion__nombre')\
            .annotate(ejecutado=Sum('ejecutado'))\
            .order_by('catinversion__nombre')
        sources = glue(tipos_inicial, tipos_final, 'catinversion__nombre')
        source_clase = None
        #source_ultimos = Proyecto.objects.values('inversion__anio').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_ultimos = Proyecto.objects.filter(
            inversion__anio__gt=year_list[-6])\
            .values('inversion__anio')\
            .annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

        # tabla2, tabla3
        cat_inicial = Proyecto.objects.filter(
            inversion__periodo=PERIODO_INICIAL, inversion__anio=year)\
            .values(
                'catinversion__nombre', 'catinversion__id',
                'catinversion__shortname', 'catinversion__color',
                'catinversion__slug')\
            .annotate(inicial_asignado=Sum('asignado'))\
            .order_by('catinversion')
        cat_actualizado = Proyecto.objects.filter(
            inversion__periodo=PERIODO_ACTUALIZADO, inversion__anio=year)\
            .values(
                'catinversion__nombre', 'catinversion__id',
                'catinversion__shortname', 'catinversion__color',
                'catinversion__slug')\
            .annotate(
                actualizado_asignado=Sum('asignado'),
                actualizado_ejecutado=Sum('ejecutado'))\
            .order_by('catinversion')
        cat_final = Proyecto.objects.filter(
            inversion__periodo=PERIODO_FINAL, inversion__anio=year)\
            .values(
                'catinversion__nombre', 'catinversion__id',
                'catinversion__shortname', 'catinversion__color',
                'catinversion__slug')\
            .annotate(
                final_asignado=Sum('asignado'),
                final_ejecutado=Sum('ejecutado'))\
            .order_by('catinversion')
        cat_periodo = Proyecto.objects.filter(
            inversion__periodo=periodo, inversion__anio=year)\
            .values(
                'catinversion__nombre', 'catinversion__id',
                'catinversion__shortname', 'catinversion__color',
                'catinversion__slug')\
            .annotate(asignado=Sum('asignado'), ejecutado=Sum('ejecutado'))\
            .order_by('catinversion')
        cat2 = superglue(
            data=(cat_inicial, cat_final),
            key='catinversion__nombre')
        cat3 = superglue(
            data=(cat_inicial, cat_final, cat_actualizado, cat_periodo),
            key='catinversion__nombre')

        # tabla4
        anual_inicial = Proyecto.objects.filter(inversion__periodo=PERIODO_INICIAL).values('inversion__anio').annotate(asignado=Sum('asignado')).order_by('inversion__anio')
        anual_actualizado = Proyecto.objects.filter(inversion__periodo=PERIODO_ACTUALIZADO).values('inversion__anio').annotate(asignado=Sum('asignado')).order_by('inversion__anio')
        anual_final = Proyecto.objects.filter(inversion__periodo=PERIODO_FINAL).values('inversion__anio').annotate(ejecutado=Sum('ejecutado')).order_by('inversion__anio')
        anual2 = glue(inicial=anual_inicial, final=anual_final, key='inversion__anio')
        anual3 = glue(inicial=anual_inicial, final=anual_final, actualizado=anual_actualizado, key='inversion__anio')

        # obtiene datos para grafico comparativo de tipo de inversions
        tipo_inicial= list(Proyecto.objects.filter(inversion__anio=year, inversion__periodo=PERIODO_INICIAL).values('catinversion__nombre').order_by('catinversion__nombre').annotate(asignado=Sum('asignado')))
        tipo_actualizado = list(Proyecto.objects.filter(inversion__anio=year, inversion__periodo=PERIODO_ACTUALIZADO).values('catinversion__nombre').annotate(asignado=Sum('asignado')))
        tipo_final = list(Proyecto.objects.filter(inversion__anio=year, inversion__periodo=PERIODO_FINAL).values('catinversion__nombre').order_by('catinversion__nombre').annotate(ejecutado=Sum('ejecutado')))
        tipo = glue(inicial=tipo_inicial, final=tipo_final, key='catinversion__nombre', actualizado=tipo_actualizado)

        # obtiene datos para grafico comparativo de area
        area_inicial= list(Proyecto.objects.filter(inversion__anio=year, inversion__periodo=PERIODO_INICIAL).values('areageografica').order_by('areageografica').annotate(asignado=Sum('asignado')))
        area_final = list(Proyecto.objects.filter(inversion__anio=year, inversion__periodo=PERIODO_FINAL).values('areageografica').order_by('areageografica').annotate(ejecutado=Sum('ejecutado')))
        area = glue(area_inicial, area_final, 'areageografica')

        # obtiene datos para grafico comparativo de fuente
        fuente_inicial= list(InversionFuenteDetalle.objects.filter(inversionfuente__anio=year, inversionfuente__periodo=PERIODO_INICIAL).values('fuente__nombre').order_by('fuente__nombre').annotate(asignado=Sum('asignado')))
        fuente_final = list(InversionFuenteDetalle.objects.filter(inversionfuente__anio=year, inversionfuente__periodo=PERIODO_FINAL).values('fuente__nombre').order_by('fuente__nombre').annotate(ejecutado=Sum('ejecutado')))
        fuente = glue(fuente_inicial, fuente_final, 'fuente__nombre')
        fuente_actual = list(InversionFuenteDetalle.objects.filter(inversionfuente__anio=year, inversionfuente__periodo=periodo).values('fuente__nombre').order_by('fuente__nombre').annotate(ejecutado=Sum(quesumar)))

        # grafico de ejecutado y asignado a nivel nacional (distintas clases) porcentage
        sql_tpl="SELECT clasificacion,\
                (SELECT SUM({quesumar}) FROM core_Proyecto JOIN core_Inversion ON core_Proyecto.inversion_id=core_Inversion.id JOIN core_CatInversion ON core_Proyecto.catinversion_id=core_CatInversion.id \
                JOIN lugar_clasificacionmunicano ON core_Inversion.municipio_id=lugar_clasificacionmunicano.municipio_id AND core_Inversion.anio=lugar_clasificacionmunicano.anio \
                WHERE core_Inversion.anio={year} AND core_Inversion.periodo='{periodo}' AND lugar_clasificacionmunicano.clasificacion_id=clase.id) /\
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

        # para luego obtener valores para este año y nada más? FIXME !
        source_inicial = Proyecto.objects.filter(inversion__periodo=PERIODO_INICIAL,).\
            values('inversion__anio').annotate(ejecutado=Sum('ejecutado'),
                                               asignado=Sum('asignado')).order_by()
        source_final = Proyecto.objects.filter(inversion__periodo=periodo,).\
            values('inversion__anio').annotate(ejecutado=Sum('ejecutado'),
                                               asignado=Sum('asignado')).order_by()

        # obtiene valores para este año de las listas
        try:
            asignado = (item for item in source_inicial
                        if item["inversion__anio"] == int(year)).next()['asignado']
        except StopIteration:
            asignado = 0
        try:
            ejecutado = (item for item in source_final
                         if item["inversion__anio"] == int(year)).next()['ejecutado']
        except StopIteration:
            ejecutado = 0
        # FIXME que es esto: ???
        source_anios = glue(source_inicial, source_final, 'inversion__anio')

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
                'names':  [u'Años',u'Actualizado',u'P. Inicial',u'Ejecutado',],
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
                    'inversion__anio': ['asignado', 'actualizado', 'ejecutado', ],
                    },
                    }],
                chart_options =
                {'title': { 'text': u'Seguimiento de las Inversiones percápita %s' % (municipio,)}},
                )
        inversion_comparativo_anios = RawDataPool(
            series=
                [{'options': {'source': anual3 },
                'names':  [u'Años',u'Actualizado',u'P. Inicial',u'Ejecutado',],
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
                    'inversion__anio': ['asignado', 'actualizado', 'ejecutado', ],
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
                'data': { 'table': 'datatable'},})
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
                  'plotOptions': { 'pie': { 'dataLabels': { 'enabled': True, 'format': '{point.percentage:.2f} %' }, 'showInLegend': True, 'depth': 35}},
                  'tooltip': { 'pointFormat': '{series.name}: <b>{point.percentage:.2f}%</b>' },
                  'colors':  colorscheme
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

    tipos = []
    for row in tipo:
        tipos.append({
          'catinversion__nombre': row['catinversion__nombre'],
          datacol: row[datacol] / 1000000,
        })

    inversion_tipo = RawDataPool(
        series=[{
            'options': {'source': tipos},
            'terms':  ['catinversion__nombre', datacol],
            }],
        )
    inversion_source = RawDataPool(
        series=[{
            'options': {'source': tipo},
            'terms':  ['catinversion__nombre', datacol],
            }]
        )
    bar = Chart(
        datasource=inversion_tipo,
        series_options=[{'options': {
            'type': 'column',
            'colorByPoint': True,
            'stacking': False},
            'terms': {
            'catinversion__nombre': [datacol],
        },
        }],
        chart_options=chart_options)

    custom_chart_options = chart_options.copy()
    custom_chart_options['tooltip']['pointFormat'] = ''
    pie = Chart(
        datasource=inversion_tipo,
        series_options=[
            {
                'options': {'type': 'pie', 'stacking': False},
                'terms': {'catinversion__nombre': [datacol]},
            }],
        chart_options=custom_chart_options)

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

    ejecutado_pie = Chart(
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
                  'plotOptions': { 'pie': { 'dataLabels': { 'enabled': True, 'format': '{point.percentage:.2f} %' }, 'showInLegend': True, 'depth': 35}},
                  'tooltip': { 'pointFormat': '{series.name}: <b>{point.percentage:.2f}%</b>' },
              })

    bar_horizontal = None

    # bar horizontal
    if otros:
        parameters = {
            'data': otros,
            'field1': 'inversion__municipio__nombre',
            'field2': '{}_percent'.format(quesumar),
            'typechart': 'bar',
            'title': "Ranking de Municipios Categoría '{}'".
            format(mi_clase.clasificacion),
            'labelX_axis': 'Municipio',
            'labelY_axis': 'Gasto por habitante',
            'pointFormat': '<span>Inversion Asignada</span>:<b>{point.y}</b>',
        }
        bar_horizontal = graphChart(parameters)
    elif porclasep:
        parameters = {
            'data': porclasep,
            'field1': 'clasificacion',
            'field2': quesumar,
            'typechart': 'column',
            'title': 'Inversión percápita',
            'labelX_axis': 'Grupos',
            'labelY_axis': 'Córdobas',
            'pointFormat': '<span>{series.name}</span>:<b>{point.y:.2f}</b>',
        }
        bar_horizontal = graphChart(parameters)

    # tabla: get total and percent
    total = {}
    # sum if not None
    total['ejecutado'] = sum(item['ejecutado'] for item in sources if item['ejecutado'])
    total['asignado'] = sum(item['asignado'] for item in sources if item['asignado'])
    for row in sources:
        row['ejecutado_percent'] = percentage(row['ejecutado'], total['ejecutado'])
        row['asignado_percent'] = percentage(row['asignado'], total['asignado'])

    # tabla: get total and percent
    #source_list = list(source)
    #total = source.aggregate(total=Sum('ejecutado'))['total']
    # for row in source:
    #    row['percent'] = round(row['ejecutado'] / total * 100, 1)

    actualizado_asignado = sum(xnumber(row.get('actualizado_asignado')) for row in cat3)

    # calculando porcentaje de cada categoria y suma total de los porcentajes
    total_asig_porcentaje = 0
    total_ejec_porcentaje = 0
    total_act_porcentaje = 0
    for row in cat3:
        row['ini_asig_porcentaje'] = percentage(row['asignado'], asignado)
        total_asig_porcentaje += row['ini_asig_porcentaje']
        row['act_porcentaje'] = percentage(row.get('actualizado_asignado'), actualizado_asignado)
        total_act_porcentaje += row['act_porcentaje']
        row['ejec_porcentaje'] = percentage(row['ejecutado'], ejecutado)
        total_ejec_porcentaje += row['ejec_porcentaje']


    if source_clase:
        total_clase = source_clase.aggregate(total=Sum('clase'))['total']
        for row in source_clase:
            row['clase_percent'] = round(row['clase'] / total_clase * 100, 1)
        for row in sources:
            for row2 in source_clase:
                if row2['catinversion__nombre'] == row['catinversion__nombre']:
                    row['clase'] = row2['clase']
                    row['clase_percent'] = row2['clase_percent']

    # tabla: get inversions por año
    porano_table = {}
    ano_table = {}
    ys = source_ultimos.order_by('catinversion__nombre').values('catinversion__nombre').distinct()
    for y in ys:
        name = y['catinversion__nombre']
        label = name if name else 'Sin Clasificar'
        porano_table[label] = {}
        for ayear in year_list:
            value = source_ultimos.filter(inversion__anio=ayear, catinversion__nombre=label).aggregate(total=Sum('asignado'))['total']
            porano_table[label][ayear] = {}
            porano_table[label][ayear]['raw'] = value if value else ''

            if not ayear in ano_table:
                ano_table[ayear] = 0
            ano_table[ayear] += value if value else 0

        if municipio and year:
            periodo = PERIODO_FINAL
            quesumar = 'ejecutado'
            value = Proyecto.objects.filter(inversion__anio=year, inversion__periodo=periodo, tipoproyecto__nombre=name, \
                    inversion__municipio__clasificaciones__clasificacion=mi_clase.clasificacion, inversion__municipio__clase__anio=year).\
                    aggregate(total=Avg(quesumar))['total']
            porano_table[name]['extra'] = value if value else '...'

    for y in ys:
        name = y['catinversion__nombre']
        label = name if name else 'Sin Clasificar'
        for ayear in year_list:
            if porano_table[label][ayear]['raw']:
                porano_table[label][ayear]['percent'] = format(
                    porano_table[label][ayear]['raw'] / ano_table[ayear], '.2%')

    charts = [pie, bar, bar_horizontal]

    return {
        'charts': charts,
        'mi_clase': mi_clase,
        'year': year,
        'porano': porano_table,
        'totales': sources,
        'cat': cat3,
        'anuales': anual3,
        'ejecutado': ejecutado,
        'ejecutado_porcentaje': total_ejec_porcentaje,
        'asignado': asignado,
        'asignado_porcentaje': total_asig_porcentaje,
        'actualizado_porcentaje': actualizado_asignado,
        'porclasep': porclasep,
        'periodo': periodo,
        'otros': otros,
        'year_list': year_list,
        'municipio_list': municipio_list,
        'periodo_list': periodo_list,
        'municipio': municipio_row}
