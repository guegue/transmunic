# -*- coding: utf-8 -*-

from itertools import chain
from datetime import datetime, time

from django.shortcuts import render_to_response
from django.db.models import Q, Sum, Max, Min

from chartit import DataPool, Chart, PivotDataPool, PivotChart, RawDataPool

from models import IngresoDetalle, Ingreso, GastoDetalle, Gasto, Inversion, Proyecto, Municipio, TipoGasto, InversionFuente, InversionFuenteDetalle, CatInversion, ClasificacionMunic
from models import Gasto_year_list, Gasto_periodos, Ingreso_year_list, Ingreso_periodos, Inversion_year_list, Inversion_periodos, InversionFuente_year_list, InversionFuente_periodos

#def inversion_minima_sector_chart(municipio=None, year=None):
def inversion_minima_sector_chart(request):
    municipio = request.GET.get('municipio', None)
    year = request.GET.get('year', None)
    municipio_list = Municipio.objects.all()
    year_list = Inversion_year_list()
    if not year:
        year = list(year_list)[-2].year
    periodo_inicial = Inversion.objects.filter(fecha__year=year).aggregate(min_fecha=Min('fecha'))['min_fecha']
    periodo_final = Inversion.objects.filter(fecha__year=year).aggregate(max_fecha=Max('fecha'))['max_fecha']

    if municipio:
        source_ejecutado = Proyecto.objects.filter(inversion__fecha=periodo_final, catinversion__minimo__gt=0, inversion__municipio__slug=municipio).values('catinversion__nombre').annotate(ejecutado=Sum('ejecutado'))
        source_asignado = Proyecto.objects.filter(inversion__fecha=periodo_inicial, catinversion__minimo__gt=0, inversion__municipio__slug=municipio).values('catinversion__nombre').annotate(asignado=Sum('asignado'))
        source = CatInversion.objects.filter(minimo__gt=0).values('nombre', 'minimo',)
        total_asignado = Proyecto.objects.filter(inversion__fecha=periodo_inicial, inversion__municipio__slug=municipio).aggregate(total=Sum('asignado'))
    else:
        source_ejecutado = Proyecto.objects.filter(inversion__fecha=periodo_final, catinversion__minimo__gt=0).values('catinversion__nombre').annotate(ejecutado=Sum('ejecutado'))
        source_asignado = Proyecto.objects.filter(inversion__fecha=periodo_inicial, catinversion__minimo__gt=0).values('catinversion__nombre').annotate(asignado=Sum('asignado'))
        source = CatInversion.objects.filter(minimo__gt=0).values('nombre', 'minimo',)
        total_asignado = Proyecto.objects.filter(inversion__fecha=periodo_inicial).aggregate(total=Sum('asignado'))

    for record in source:
        record['ejecutado'] = source_ejecutado.filter(catinversion__nombre=record['nombre'])[0]['ejecutado']
        record['asignado'] = source_asignado.filter(catinversion__nombre=record['nombre'])[0]['asignado']
        record['minimo'] = total_asignado['total'] * (record['minimo']/100)
    data = RawDataPool(
           series=
            [{'options': {'source': source },
              'terms': [
                'nombre',
                'minimo',
                'ejecutado',
                'asignado',
                ]}
             ])

    chart = Chart(
            datasource = data,
            series_options =
              [{'options':{ 'type': 'column', },
                'terms':{ 'nombre': [ 'asignado', 'ejecutado', 'minimo', ] }
              }],
            chart_options =
              {'title': {
                  'text': u'Gasto mínimo por sector %s %s' % (municipio, year,)},
              })
    #return {'charts': (chart,), 'year_list': year_list, 'municipio_list': municipio_list}
    return render_to_response('chart.html',{'charts': (chart,), 'year_list': year_list, 'municipio_list': municipio_list})



def fuentes_chart(municipio=None,year=None):
    municipio_list = Municipio.objects.all()
    year_list = InversionFuente_year_list()
    if not year:
        year = list(year_list)[-1].year
    periodos = InversionFuente_periodos()
    periodo = InversionFuente.objects.filter(fecha__year=year).aggregate(max_fecha=Max('fecha'))['max_fecha']
    if municipio:
        source = InversionFuenteDetalle.objects.filter(inversionfuente__municipio__slug=municipio, inversionfuente__fecha=periodo).\
                values('fuente').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('fuente__nombre')
    else:
        source = InversionFuenteDetalle.objects.filter(inversionfuente__fecha=periodo).\
                values('fuente').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('fuente__nombre')
        source_portada = InversionFuenteDetalle.objects.filter(inversionfuente__fecha=periodo).\
                values('fuente__tipofuente__nombre').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('fuente__tipofuente__nombre')

    data = DataPool(series = [{'options': {'source': source }, 'terms': ['fuente__nombre', 'ejecutado', 'asignado', ]}])
    data_portada = DataPool(series = [{'options': {'source': source_portada }, 'terms': ['fuente__tipofuente__nombre', 'ejecutado', 'asignado', ]}])
    asignado = Chart(
            datasource = data,
            series_options =
              [{'options':{'type': 'pie'},
                'terms':{'fuente__nombre': ['asignado']}
              }],
            chart_options =
              {'title': {
                  'text': 'InversionFuente asignados: %s %s' % (municipio, year,)},
                  'plotOptions': { 'pie': { 'dataLabels': { 'enabled': False }, 'showInLegend': True, }},
              })
    asignado_portada = Chart(
            datasource = data_portada,
            series_options =
              [{'options':{'type': 'pie'},
                'terms':{'fuente__tipofuente__nombre': ['asignado']}
              }],
            chart_options =
              {'title': {
                  'text': 'InversionFuente asignados: %s %s' % (municipio, year,)},
                  'plotOptions': { 'pie': { 'dataLabels': { 'enabled': False }, 'showInLegend': True, }},
              })
    return {'charts': (asignado, asignado_portada), 'year_list': year_list, 'municipio_list': municipio_list}

def inversion_chart(municipio=None):
    municipio_list = Municipio.objects.all()
    year_list = Inversion_year_list()
    periodos = Inversion_periodos()

    if municipio:
        source = Proyecto.objects.filter(inversion__fecha__in=periodos, inversion__municipio__slug=municipio). \
            values('inversion__fecha').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_ultimos = Proyecto.objects.filter(inversion__fecha__in=periodos, inversion__municipio__slug=municipio, \
            inversion__fecha__gt=list(year_list)[-3]). \
            values('inversion__fecha').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
    else:
        source = Proyecto.objects.filter(inversion__fecha__in=periodos). \
            values('inversion__fecha').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_ultimos = Proyecto.objects.filter(inversion__fecha__in=periodos, inversion__fecha__gt=list(year_list)[-3]). \
            values('inversion__fecha').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

    data_ultimos = DataPool(
           series=
            [{'options': {
                'source': source_ultimos,
                'categories': 'inversion__fecha',
                },
              'terms': ['inversion__fecha', 'ejecutado', 'asignado',]
            }],
    )
    chart_ultimos = Chart(
            datasource = data_ultimos,
            series_options =
              [{'options':{
                  'type': 'bar',
                  'stacking': False},
                'terms': {'inversion__fecha': ['asignado', 'ejecutado']}
                }],
            chart_options =
              {'title': {'text': u'Inversión por últimos años %s' % (municipio, )}},
            x_sortf_mapf_mts = (None, lambda i:  i.strftime('%Y'), False)
    )
    data = DataPool(
           series=
            [{'options': {
                'source': source,
                'categories': 'inversion__fecha',
                },
              'terms': ['inversion__fecha', 'ejecutado', 'asignado',]
            }],
    )
    chart = Chart(
            datasource = data,
            series_options =
              [{'options':{
                  'type': 'bar',
                  'stacking': False},
                'terms': {'inversion__fecha': ['asignado', 'ejecutado']}
                }],
            chart_options =
              {'title': {'text': u'Inversión por años %s' % (municipio, )}},
            x_sortf_mapf_mts = (None, lambda i:  i.strftime('%Y'), False)
    )
    return {'charts': (chart, chart_ultimos), 'municipio_list': municipio_list}


def inversion_area_chart(municipio=None):
    municipio_list = Municipio.objects.all()
    year_list = Inversion_year_list()
    periodos = Inversion_periodos()

    if municipio:
        source = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__fecha__in=periodos)
        q = Q()
        for y in list(year_list)[-3:]:
            q |= Q(inversion__fecha__year=y.year)
        source_barra = Proyecto.objects.filter(q, inversion__municipio__slug=municipio, inversion__fecha__in=periodos)
    else:
        source = Proyecto.objects.filter(inversion__fecha__in=periodos)
        q = Q()
        for y in list(year_list)[-3:]:
            q |= Q(inversion__fecha__year=y.year)
        source_barra = Proyecto.objects.filter(q, inversion__fecha__in=periodos)

    data_barra = PivotDataPool(
           series=
            [{'options': {
                'source': source_barra,
                'categories': 'inversion__fecha',
                'legend_by': ['areageografica'],
                },
              'terms': {
                'sum_ejecutado':Sum('ejecutado'),
                'sum_asignado':Sum('asignado'),
                }}
             ],
             sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
    )
    barra = PivotChart(
            datasource = data_barra,
            series_options =
              [{'options':{
                  'type': 'bar',
                },
                'terms':['sum_ejecutado']}],
            chart_options =
              {'title': {'text': u'Inversión por área %s' % (municipio, )}},
    )
    data = PivotDataPool(
           series=
            [{'options': {
                'source': source,
                'categories': 'inversion__fecha',
                'legend_by': ['areageografica'],
                },
              'terms': {
                'sum_ejecutado':Sum('ejecutado'),
                'sum_asignado':Sum('asignado'),
                }}
             ],
             sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
    )
    chart = PivotChart(
            datasource = data,
            series_options =
              [{'options':{
                  'type': 'bar',
                },
                'terms':['sum_ejecutado']}],
            chart_options =
              {'title': {'text': u'Inversión por área %s' % (municipio, )}},
    )
    return {'charts': (chart, barra,), 'municipio_list': municipio_list}

def ep_chart(request):
    municipio_list = Municipio.objects.all()
    year_list = Ingreso_year_list()
    periodos = Ingreso_periodos()
    municipio = request.GET.get('municipio','')
    if municipio:
        with open ("core/ep_municipio.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [municipio, municipio, periodos])
    else:
        with open ("core/ep.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [periodos])
    data = RawDataPool(
           series=
            [{'options': {'source': source },
              'terms': [
                'fecha',
                'ejecutado',
                ]}
             ])

    bar = Chart(
            datasource = data,
            series_options =
              [{'options':{
                  'type': 'bar',},
                'terms':{
                  'fecha': [
                    'ejecutado']
                  }}],
            chart_options = {
                'title': {
                  'text': u'Ejecución del presupuesto %s ' % (municipio,)},
                },
            x_sortf_mapf_mts = (None, lambda i:  i.strftime('%Y'), False)
            )

    return render_to_response('agochart.html',{'charts': (bar, ), 'municipio_list': municipio_list})

def psd_chart(request):
    municipio_list = Municipio.objects.all()
    year_list = Ingreso_year_list()
    periodos = list(Ingreso_periodos())[:-1]
    municipio = request.GET.get('municipio','')
    if municipio:
        with open ("core/psd_municipio.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [municipio, municipio, municipio, municipio, periodos])
    else:
        with open ("core/psd.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [periodos])
    data = RawDataPool(
           series=
            [{'options': {'source': source },
              'terms': [
                'fecha',
                'ejecutado',
                'asignado',
                ]}
             ])

    bar = Chart(
            datasource = data,
            series_options =
              [{'options':{
                  'type': 'bar',},
                'terms':{
                  'fecha': [
                    'asignado',
                    'ejecutado']
                  }}],
            chart_options = {
                'title': {
                  'text': u'Peso del servicio de la deuda %s ' % (municipio,)},
                },
            x_sortf_mapf_mts = (None, lambda i:  i.strftime('%Y'), False)
            )

    return render_to_response('agochart.html',{'charts': (bar, ), 'municipio_list': municipio_list})

def aci_chart(request):
    municipio_list = Municipio.objects.all()
    year_list = Ingreso_year_list()
    periodos = Ingreso_periodos()
    municipio = request.GET.get('municipio','')
    if municipio:
        with open ("core/aci_municipio.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [municipio, municipio, municipio, municipio, municipio, municipio, periodos])
    else:
        with open ("core/aci.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [periodos])
    data = RawDataPool(
           series=
            [{'options': {'source': source },
              'terms': [
                'fecha',
                'ejecutado',
                'asignado',
                ]}
             ])

    bar = Chart(
            datasource = data,
            series_options =
              [{'options':{
                  'type': 'bar',},
                'terms':{
                  'fecha': [
                    'asignado',
                    'ejecutado']
                  }}],
            chart_options = {
                'title': {
                  'text': u'Ahorro corriente para inversiones %s ' % (municipio,)},
                },
            x_sortf_mapf_mts = (None, lambda i:  i.strftime('%Y'), False)
            )

    return render_to_response('agochart.html',{'charts': (bar, ), 'municipio_list': municipio_list})


def ago_chart(request):
    municipio_list = Municipio.objects.all()
    year_list = Ingreso_year_list()
    periodos = list(Ingreso_periodos())[:-1]
    municipio = request.GET.get('municipio','')

    if municipio:
        with open ("core/ago_municipio.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [municipio, municipio, municipio, municipio, municipio, municipio, periodos])
    else:
        with open ("core/ago.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [periodos])

    data = RawDataPool(
           series=
            [{'options': {'source': source },
              'terms': [
                'fecha',
                'ejecutado',
                'asignado',
                ]}
             ])

    bar = Chart(
            datasource = data,
            series_options =
              [{'options':{
                  'type': 'bar',},
                'terms':{
                  'fecha': [
                    'asignado',
                    'ejecutado']
                  }}],
            chart_options = {
                'title': {
                  'text': u'Autonomía %s ' % (municipio,)},
                },
                x_sortf_mapf_mts = (None, lambda i:  i.strftime('%Y'), False)
            )

    return render_to_response('agochart.html',{'charts': (bar, ), 'municipio_list': municipio_list})

def gpersonal_chart(request):
    municipio_list = Municipio.objects.all()
    year_list = Gasto_year_list()
    periodos = Gasto_periodos()
    municipio = request.GET.get('municipio','')
    year_list = Gasto_year_list()
    periodos = Gasto_periodos()
    year = request.GET.get('year', None)
    if not year:
        year = list(year_list)[-2].year

    if municipio:
        source_barra = GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__fecha__in=periodos, tipogasto=TipoGasto.PERSONAL)
        source_ejecutado = GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__fecha__in=periodos, tipogasto=TipoGasto.PERSONAL).exclude(gasto__fecha__year=year)
    else:
        source_barra = GastoDetalle.objects.filter(gasto__fecha__in=periodos, tipogasto=TipoGasto.PERSONAL)
        source_ejecutado = GastoDetalle.objects.filter(gasto__fecha__in=periodos, tipogasto=TipoGasto.PERSONAL).exclude(gasto__fecha__year=year)

        # chart: porcentage gastos de personal
        periodo_inicial = Gasto.objects.filter(fecha__year=year).aggregate(min_fecha=Min('fecha'))['min_fecha']
        source_pgp_asignado =  GastoDetalle.objects.filter(gasto__fecha=periodo_inicial, tipogasto=TipoGasto.PERSONAL).aggregate(asignado=Sum('asignado'))
        source_pgp_asignado['nombre'] = 'Personal'
        otros_asignado = GastoDetalle.objects.filter(gasto__fecha=periodo_inicial).exclude(tipogasto=TipoGasto.PERSONAL).aggregate(asignado=Sum('asignado'))
        otros_asignado['nombre'] = 'Otros'
        source_pgp = [source_pgp_asignado, otros_asignado]
        print source_pgp

    data_pgf = RawDataPool(
           series = [{
              'options': {'source': source_pgp },
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
            },
    )
    data_ejecutado = PivotDataPool(
           series=
            [{'options': {
                'source': source_ejecutado,
                'categories': 'gasto__fecha',
                'legend_by': 'subtipogasto__nombre',
                },
              'terms': {
                'sum_ejecutado':Sum('ejecutado'),
                }}
             ],
             sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
    )
    chart_ejecutado = PivotChart(
            datasource = data_ejecutado,
            series_options =
              [{'options':{
                  'type': 'area',
                  'stacking': True},
                'terms':['sum_ejecutado']}],
            chart_options =
              {'title': {'text': 'Gastos ejecutados personal: %s' % (municipio, )}},
    )
    data = PivotDataPool(
           series=
            [{'options': {
                'source': source_barra,
                'categories': 'gasto__fecha',
                'legend_by': 'subtipogasto__nombre',
                },
              'terms': {
                'sum_asignado':Sum('asignado'),
                }}
             ],
             sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
    )
    chart = PivotChart(
            datasource = data,
            series_options =
              [{'options':{
                  'type': 'area',
                  'stacking': True},
                'terms':['sum_asignado']}],
            chart_options =
              {'title': {'text': 'Gastos asignados personal: %s' % (municipio, )}},
    )
    return render_to_response('gpersonal.html',{'charts': (chart, chart_ejecutado, pie), 'municipio_list': municipio_list, 'year_list': year_list})

def gf_chart(request):
    municipio_list = Municipio.objects.all()
    municipio = request.GET.get('municipio', None)
    year_list = Gasto_year_list()
    periodos_iniciales = Gasto_periodos(inicial=True)
    periodos_finales = Gasto_periodos()
    year = request.GET.get('year', None)
    if not year:
        year = list(year_list)[-2].year
    periodo_inicial = Gasto.objects.filter(fecha__year=year).aggregate(min_fecha=Min('fecha'))['min_fecha']

    if municipio:
        source_inicial = GastoDetalle.objects.filter(gasto__fecha__in=periodos_iniciales, \
            tipogasto__clasificacion=TipoGasto.CORRIENTE, gasto__municipio__slug=municipio).\
            values('gasto__fecha').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_final = GastoDetalle.objects.filter(gasto__fecha__in=periodos_finales, \
            tipogasto__clasificacion=TipoGasto.CORRIENTE, gasto__municipio__slug=municipio).\
            values('gasto__fecha').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        mi_gasto_promedio = GastoDetalle.objects.filter(tipogasto__clasificacion=TipoGasto.CORRIENTE, gasto__municipio__slug=municipio).aggregate(asignado=Sum('asignado'))['asignado']
        mi_clasificacion = ClasificacionMunic.objects.filter(desde__lt=mi_gasto_promedio, hasta__gt=mi_gasto_promedio)
        gasto_promedio = GastoDetalle.objects.filter(gasto__fecha__in=periodos_finales, \
            tipogasto__clasificacion=TipoGasto.CORRIENTE, gasto__municipio__clasificacionmunic=mi_clasificacion). \
            values('gasto__fecha').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        for record in source_inicial:
            record['ejecutado'] = source_final.filter(gasto__fecha__year=record['gasto__fecha'].year)[0]['ejecutado']
            record['promedio'] = gasto_promedio.filter(gasto__fecha__year=record['gasto__fecha'].year)[0]['asignado']
        source = source_inicial
        print source
            
        # FIXME. igual que abajo (sin municipio) de donde tomar los datos?
        source_barra = GastoDetalle.objects.filter( gasto__fecha__in=periodos_iniciales, \
            tipogasto__clasificacion=TipoGasto.CORRIENTE, gasto__municipio__slug=municipio).\
            values('gasto__fecha').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_barra_final = source_barra # FIXME este es un work-around

        # chart: porcentage gastos de funcionamiento
        source_pgf_asignado =  GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__fecha=periodo_inicial, tipogasto__clasificacion=TipoGasto.CORRIENTE).aggregate(asignado=Sum('asignado'))
        source_pgf_asignado['nombre'] = 'Funcionamiento'
        otros_asignado = GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__fecha=periodo_inicial).exclude(tipogasto__clasificacion=TipoGasto.CORRIENTE).aggregate(asignado=Sum('asignado'))
        otros_asignado['nombre'] = 'Otros'
        source_pgf = [source_pgf_asignado, otros_asignado]
    else:
        source_inicial = GastoDetalle.objects.filter(gasto__fecha__in=periodos_iniciales, \
            tipogasto__clasificacion=TipoGasto.CORRIENTE).\
            values('gasto__fecha').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_final = GastoDetalle.objects.filter(gasto__fecha__in=periodos_finales, \
            tipogasto__clasificacion=TipoGasto.CORRIENTE).\
            values('gasto__fecha').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        for record in source_inicial:
            record['ejecutado'] = source_final.filter(gasto__fecha__year=record['gasto__fecha'].year)[0]['ejecutado']
        source = source_inicial

        # FIXME. en el grafico de periodos...  de donde tomar los datos?
        source_barra_inicial = GastoDetalle.objects.filter(gasto__fecha__in=periodos_iniciales, \
            tipogasto__clasificacion=TipoGasto.CORRIENTE).\
            values('gasto__fecha').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_barra_final = GastoDetalle.objects.filter(gasto__fecha__in=periodos_finales, \
            tipogasto__clasificacion=TipoGasto.CORRIENTE).\
            values('gasto__fecha').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

        # chart: porcentage gastos de funcionamiento
        source_pgf_asignado =  GastoDetalle.objects.filter(gasto__fecha=periodo_inicial, tipogasto__clasificacion=TipoGasto.CORRIENTE).aggregate(asignado=Sum('asignado'))
        source_pgf_asignado['nombre'] = 'Funcionamiento'
        otros_asignado = GastoDetalle.objects.filter(gasto__fecha=periodo_inicial).exclude(tipogasto__clasificacion=TipoGasto.CORRIENTE).aggregate(asignado=Sum('asignado'))
        otros_asignado['nombre'] = 'Otros'
        source_pgf = [source_pgf_asignado, otros_asignado]

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
                'title': {'text': 'Gastos de funcionamiento %s %s ' % (municipio, year,)},
            },
    )
    data_barra = DataPool(
           series = [{
              'options': {'source': source_barra_final },
              'terms': [ 'gasto__fecha', 'ejecutado', 'asignado', ]
            }]
    )

    barra = Chart(
            datasource = data_barra,
            series_options =
              [{'options':{
                  'type': 'column',},
                'terms':{
                  'gasto__fecha': [
                    'asignado',
                    'ejecutado']
                  }}],
            chart_options = {
                'title': {'text': 'Gastos de funcionamiento %s ' % (municipio,)},
                },
            )
    dataterms = ['gasto__fecha', 'asignado', 'ejecutado']
    terms = ['asignado', 'ejecutado']
    if municipio:
        dataterms = ['gasto__fecha', 'asignado', 'ejecutado', 'promedio']
        terms = ['asignado', 'ejecutado', 'promedio',]

    data = RawDataPool(series = [{'options': {'source': source }, 'terms': dataterms}])
    gfbar = Chart(
            datasource = data,
            series_options = [{'options': {'type': 'column'}, 'terms': {'gasto__fecha': terms }}],
            chart_options = {'title': {'text': u'Gastos de funcionamiento año %s ' % (municipio,)}},
            x_sortf_mapf_mts = (None, lambda i:  i.strftime('%Y'), False)
            )

    return render_to_response('gfchart.html',{'charts': (gfbar, barra, pie), 'municipio_list': municipio_list})


def inversion_categoria_chart(request):
    municipio_list = Municipio.objects.all()
    year_list = Inversion_year_list()
    year = list(year_list)[-1].year
    municipio = request.GET.get('municipio','')
    periodo = Inversion.objects.filter(fecha__year=year).aggregate(max_fecha=Max('fecha'))['max_fecha']

    if municipio:
        source = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__fecha=periodo).values('catinversion').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('catinversion')
        source_ultimos = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__fecha__gt=list(year_list)[-3]). \
            values('inversion__fecha').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
    else:
        source = Proyecto.objects.filter(inversion__fecha=periodo).values('catinversion').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('catinversion')
        source_ultimos = Proyecto.objects.filter(inversion__fecha__gt=list(year_list)[-3]). \
            values('inversion__fecha').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

    data_ultimos = DataPool(
           series=
            [{'options': {
                'source': source_ultimos,
                'categories': 'inversion__fecha',
                },
              'terms': ['inversion__fecha', 'ejecutado', 'asignado',]
            }],
    )
    ultimos = Chart(
            datasource = data_ultimos,
            series_options =
              [{'options':{
                  'type': 'bar',
                  'stacking': False},
                'terms': {'inversion__fecha': ['asignado', 'ejecutado']}
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
                'asignado',
                ]}
             ])

    asignado = Chart(
            datasource = oimdata,
            series_options =
              [{'options':{
                  'type': 'pie',
                  },
                'terms':{
                  'catinversion__nombre': [
                    'asignado']
                  }}],
            chart_options =
              {'title': {
                  'text': 'Inversion asignados: %s %s' % (municipio, year,)},
                  'plotOptions': { 'pie': { 'dataLabels': { 'enabled': False }, 'showInLegend': True, }},
              })

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
                  'text': 'Inversion ejecutados: %s %s' % (municipio, year,)},
                  'plotOptions': { 'pie': { 'dataLabels': { 'enabled': False }, 'showInLegend': True, }},
              })

    return render_to_response('inversionpiechart.html',{'charts': (ejecutado, asignado, ultimos), 'year_list': year_list, 'municipio_list': municipio_list})

def ogm_chart(municipio=None, year=None):
    municipio_list = Municipio.objects.all()
    year_list = Gasto_year_list()
    if not year:
        year = list(year_list)[-1].year
    periodo = Gasto.objects.filter(fecha__year=year).aggregate(max_fecha=Max('fecha'))['max_fecha']
    periodos = Gasto_periodos()

    if municipio:
        source = GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__fecha=periodo).values('tipogasto').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('tipogasto__nombre')
        q = Q()
        for y in list(year_list)[-3:]:
            q |= Q(gasto__fecha__year=y.year)
        source_barra = GastoDetalle.objects.filter(q, gasto__municipio__slug=municipio)
        source_pivot = GastoDetalle.objects.filter(gasto__fecha__in=periodos, gasto__municipio__slug=municipio)
    else:
        source = GastoDetalle.objects.filter(gasto__fecha=periodo).values('tipogasto').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('tipogasto__nombre')
        q = Q()
        for y in list(year_list)[-3:]:
            q |= Q(gasto__fecha__year=y.year)
        source_barra = GastoDetalle.objects.filter(q)
        source_pivot = GastoDetalle.objects.filter(gasto__fecha__in=periodos)


    pivot_barra = PivotDataPool(
           series=
            [{'options': {'source': source_pivot,
                        'categories': 'gasto__fecha',
                        'legend_by': 'tipogasto__nombre', },
              'terms': {
                  'ejecutado':Sum('ejecutado'),
                  'asignado':Sum('asignado'),
                }
              }],
            sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
            )
    asignado_barra = PivotChart(
            datasource = pivot_barra,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': 'percent'},
                'terms':['asignado']
                }],
            chart_options =
              {'title': { 'text': 'Gastos asignados por tipo %s' % (municipio,)}},
            )
    ogmdata_barra = PivotDataPool(
           series=
            [{'options': {'source': source_barra,
                        'categories': 'gasto__fecha',
                         },
              'terms': {
                  'ejecutado':Sum('ejecutado'),
                  'asignado':Sum('asignado'),
                }
              }],
            )
    barra = PivotChart(
            datasource = ogmdata_barra,
            series_options =
              [{'options':{
                  'type': 'column',
                },
                'terms':['asignado','ejecutado']
                }],
            chart_options =
              {'title': { 'text': 'Gastos por periodo %s' % (municipio,)}},
            )
    ogmdata = DataPool(
           series=
            [{'options': {'source': source },
              'terms': [
                'tipogasto__nombre',
                'ejecutado',
                'asignado',
                ]}
             ])

    asignado = Chart(
            datasource = ogmdata,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'tipogasto__nombre': [
                    'asignado']
                  }}],
            chart_options =
              {'title': {
                  'text': 'Gastos asignados: %s %s' % (municipio, year,)},
                  'plotOptions': { 'pie': { 'dataLabels': { 'enabled': False }, 'showInLegend': True, }},
              })

    ejecutado = Chart(
            datasource = ogmdata,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'tipogasto__nombre': [
                    'ejecutado']
                  }}],
            chart_options =
              {
                  'title': {'text': 'Gastos ejecutados: %s %s' % (municipio, year,)},
                  'plotOptions': { 'pie': { 'dataLabels': { 'enabled': False }, 'showInLegend': True, }},
              })

    return {'charts': (ejecutado, asignado, asignado_barra, barra), 'year_list': year_list, 'municipio_list': municipio_list}

def oim_chart(municipio=None, year=None):
    municipio_list = Municipio.objects.all()
    year_list = Ingreso_year_list()
    if not year:
        year = list(year_list)[-1].year
    periodo = Ingreso.objects.filter(fecha__year=year).aggregate(max_fecha=Max('fecha'))['max_fecha']
    periodos = Ingreso_periodos()

    if municipio:
        source = IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio, ingreso__fecha=periodo).values('subsubtipoingreso__origen').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('subsubtipoingreso__origen')
        source_barra = IngresoDetalle.objects.filter(ingreso__fecha__in=periodos, ingreso__municipio__slug=municipio)
        q = Q()
        for y in list(year_list)[-3:]:
            q |= Q(ingreso__fecha__year=y.year)
        source_barra2 = IngresoDetalle.objects.filter(q, ingreso__municipio__slug=municipio)
    else:
        source = IngresoDetalle.objects.filter(ingreso__fecha=periodo).values('subsubtipoingreso__origen').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('subsubtipoingreso__origen')
        source_barra = IngresoDetalle.objects.filter(ingreso__fecha__in=periodos)
        source_barra2 = IngresoDetalle.objects.filter(ingreso__fecha__gt=list(year_list)[-3])

    oimdata_barra = PivotDataPool(
           series=
            [{'options': {'source': source_barra,
                        'categories': 'ingreso__fecha',
                        'legend_by': 'subsubtipoingreso__origen__nombre', },
              'terms': {
                  'ejecutado':Sum('ejecutado'),
                  'asignado':Sum('asignado'),
                }
              }],
            sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
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
                        'categories': 'ingreso__fecha',
                         },
              'terms': {
                  'ejecutado':Sum('ejecutado'),
                  'asignado':Sum('asignado'),
                }
              }],
            )
    barra2 = PivotChart(
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
                'ejecutado',
                'asignado',
                ]}
             ])

    asignado = Chart(
            datasource = oimdata,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'subsubtipoingreso__origen__nombre': [
                    'asignado']
                  }}],
            chart_options =
              {'title': {
                  'text': 'Ingresos asignados: %s %s' % (municipio, year,)},
                  'plotOptions': { 'pie': { 'dataLabels': { 'enabled': False }, 'showInLegend': True, }},
              })

    ejecutado = Chart(
            datasource = oimdata,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'subsubtipoingreso__origen__nombre': [
                    'ejecutado']
                  }}],
            chart_options =
              {
                  'title': {'text': 'Ingresos ejecutados: %s %s' % (municipio, year,)},
                  'plotOptions': { 'pie': { 'dataLabels': { 'enabled': False }, 'showInLegend': True, }},
              }
    )

    return {'charts': (ejecutado, asignado, asignado_barra, barra2), 'year_list': year_list, 'municipio_list': municipio_list}
