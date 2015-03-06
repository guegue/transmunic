# -*- coding: utf-8 -*-

from datetime import datetime, time

from django.shortcuts import render_to_response
from django.db.models import Q, Sum, Max

from chartit import DataPool, Chart, PivotDataPool, PivotChart, RawDataPool

from models import IngresoDetalle, Ingreso, GastoDetalle, Gasto, Inversion, Proyecto, Municipio, TipoGasto
from models import Gasto_year_list, Gasto_periodos, Ingreso_year_list, Ingreso_periodos, Inversion_year_list, Inversion_periodos

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
    actual='2015'

    if municipio:
        source_barra = GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__fecha__in=periodos, tipogasto=1000000)
        source_ejecutado = GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__fecha__in=periodos, tipogasto=1000000).exclude(gasto__fecha__year=actual)
    else:
        source_barra = GastoDetalle.objects.filter(gasto__fecha__in=periodos, tipogasto=1000000)
        source_ejecutado = GastoDetalle.objects.filter(gasto__fecha__in=periodos, tipogasto=1000000).exclude(gasto__fecha__year=actual)

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
    return render_to_response('gpersonal.html',{'charts': (chart, chart_ejecutado), 'municipio_list': municipio_list})

def gf_chart(request):
    municipio_list = Municipio.objects.all()
    year_list = Gasto_year_list()
    periodos = Gasto_periodos()
    municipio = request.GET.get('municipio','')
    if municipio:
        source = GastoDetalle.objects.filter(gasto__fecha__in=periodos, \
            tipogasto__clasificacion=TipoGasto.CORRIENTE, gasto__municipio__slug=municipio).\
            values('gasto__fecha').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        q = Q()
        for y in list(year_list)[-3:]:
            q |= Q(gasto__fecha__year=y.year)
        source_barra = GastoDetalle.objects.filter(q, \
            tipogasto__clasificacion=TipoGasto.CORRIENTE, gasto__municipio__slug=municipio).\
            values('gasto__fecha').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
    else:
        source = GastoDetalle.objects.filter(gasto__fecha__in=periodos, \
            tipogasto__clasificacion=TipoGasto.CORRIENTE).\
            values('gasto__fecha').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        q = Q()
        for y in list(year_list)[-3:]:
            q |= Q(gasto__fecha__year=y.year)
        source_barra = GastoDetalle.objects.filter(q, \
            tipogasto__clasificacion=TipoGasto.CORRIENTE).\
            values('gasto__fecha').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

    data_barra = DataPool(
           series=
            [{'options': {'source': source_barra },
              'terms': [
                'gasto__fecha',
                'ejecutado',
                'asignado',
                ]}
             ])

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
    data = DataPool(
           series=
            [{'options': {'source': source },
              'terms': [
                'gasto__fecha',
                'ejecutado',
                'asignado',
                ]}
             ])

    gfbar = Chart(
            datasource = data,
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
            x_sortf_mapf_mts = (None, lambda i:  i.strftime('%Y'), False)
            )

    return render_to_response('gfchart.html',{'charts': (gfbar, barra,), 'municipio_list': municipio_list})


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

    if municipio:
        source = GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__fecha=periodo).values('subsubtipogasto__origen').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('subsubtipogasto__origen')
        q = Q()
        for y in list(year_list)[-3:]:
            q |= Q(gasto__fecha__year=y.year)
        source_barra = GastoDetalle.objects.filter(q, gasto__municipio__slug=municipio)
    else:
        source = GastoDetalle.objects.filter(gasto__fecha=periodo).values('subsubtipogasto__origen').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('subsubtipogasto__origen')
        q = Q()
        for y in list(year_list)[-3:]:
            q |= Q(gasto__fecha__year=y.year)
        source_barra = GastoDetalle.objects.filter(q)


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
                'subsubtipogasto__origen__nombre',
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
                  'subsubtipogasto__origen__nombre': [
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
                  'subsubtipogasto__origen__nombre': [
                    'ejecutado']
                  }}],
            chart_options =
              {
                  'title': {'text': 'Gastos ejecutados: %s %s' % (municipio, year,)},
                  'plotOptions': { 'pie': { 'dataLabels': { 'enabled': False }, 'showInLegend': True, }},
              })

    return {'charts': (ejecutado, asignado, barra), 'year_list': year_list, 'municipio_list': municipio_list}

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
        #source_barra2 = IngresoDetalle.objects.filter(ingreso__fecha__year__in=list(year_list)[-3:])
        q = Q()
        for y in list(year_list)[-3:]:
            q |= Q(ingreso__fecha__year=y.year)
        source_barra2 = IngresoDetalle.objects.filter(q)

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
              {'title': { 'text': 'Ingresos asignados %s' % (municipio,)}},
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
