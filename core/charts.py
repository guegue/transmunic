# -*- coding: utf-8 -*-

from datetime import datetime, time

from django.shortcuts import render_to_response
from django.db.models import Sum, Max

from chartit import DataPool, Chart, PivotDataPool, PivotChart, RawDataPool

from models import IngresoDetalle, Ingreso, GastoDetalle, Gasto, Inversion, Proyecto, Municipio, TipoGasto
from models import Gasto_year_list, Gasto_periodos, Ingreso_year_list, Ingreso_periodos, Inversion_year_list, Inversion_periodos

def inversion(request):
    municipio_list = Municipio.objects.all()
    periodos = Inversion_periodos()
    municipio = request.GET.get('municipio','')

    if municipio:
        source = Proyecto.objects.filter(inversion__fecha__in=periodos, inversion__municipio__slug=municipio). \
            values('inversion__fecha').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
    else:
        source = Proyecto.objects.filter(inversion__fecha__in=periodos). \
            values('inversion__fecha').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

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
                  'stacking': True},
                'terms': {'inversion__fecha': ['asignado', 'ejecutado']}
                }],
            chart_options =
              {'title': {
                   'text': u'Inversión por años %s' % (municipio, )},
              },
            x_sortf_mapf_mts = (None, lambda i:  i.strftime('%Y'), False)
    )
    return render_to_response('gpersonal.html',{'charts': (chart, ), 'municipio_list': municipio_list})


def inversion_area_chart(request):
    municipio_list = Municipio.objects.all()
    periodos = Inversion_periodos()
    municipio = request.GET.get('municipio','')

    if municipio:
        source = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__fecha__in=periodos)
    else:
        source = Proyecto.objects.filter(inversion__fecha__in=periodos)

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
                  'stacking': True},
                'terms':['sum_ejecutado']}],
            chart_options =
              {'title': {
                   'text': u'Inversión por área %s' % (municipio, )},
              },
    )
    return render_to_response('gpersonal.html',{'charts': (chart, ), 'municipio_list': municipio_list})

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
    periodos = Ingreso_periodos()
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
    periodos = Ingreso_periodos()
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

    if municipio:
        source_barra = GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__fecha__in=periodos, tipogasto=1000000)
    else:
        source_barra = GastoDetalle.objects.filter(gasto__fecha__in=periodos, tipogasto=1000000)

    data = PivotDataPool(
           series=
            [{'options': {
                'source': source_barra,
                'categories': 'gasto__fecha',
                'legend_by': 'subtipogasto__nombre',
                },
              'terms': {
                'sum_ejecutado':Sum('ejecutado'),
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
                'terms':['sum_ejecutado']}],
            chart_options =
              {'title': {
                   'text': 'Gastos personal: %s' % (municipio, )},
              },
    )
    return render_to_response('gpersonal.html',{'charts': (chart, ), 'municipio_list': municipio_list})

def gf_chart(request):
    municipio_list = Municipio.objects.all()
    year_list = Gasto_year_list()
    periodos = Gasto_periodos()
    municipio = request.GET.get('municipio','')
    if municipio:
        source = GastoDetalle.objects.filter(gasto__fecha__in=periodos, \
            tipogasto__clasificacion=TipoGasto.CORRIENTE, gasto__municipio__slug=municipio).\
            extra(select={'year': "EXTRACT('year' FROM fecha)"}).\
            values('gasto__fecha','year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
    else:
        source = GastoDetalle.objects.filter(gasto__fecha__in=periodos, \
            tipogasto__clasificacion=TipoGasto.CORRIENTE).\
            extra(select={'year': "EXTRACT('year' FROM fecha)"}).\
            values('gasto__fecha', 'year').\
            annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

    oimdata = DataPool(
           series=
            [{'options': {'source': source },
              'terms': [
                'gasto__fecha',
                'ejecutado',
                'asignado',
                ]}
             ])

    gfbar = Chart(
            datasource = oimdata,
            series_options =
              [{'options':{
                  'type': 'column',},
                'terms':{
                  'gasto__fecha': [
                    'asignado',
                    'ejecutado']
                  }}],
            chart_options = {
                #'xAxis': { 'type': 'datetime', 'labels': { 'formatter': 'getYear' } },
                'title': {
                  'text': 'Gastos de funcionamiento %s ' % (municipio,)},
                },
            x_sortf_mapf_mts = (None, lambda i:  i.strftime('%Y'), False)
            )

    return render_to_response('gfchart.html',{'charts': (gfbar, ), 'municipio_list': municipio_list})


def inversion_categoria_chart(request):
    municipio_list = Municipio.objects.all()
    year_list = Inversion.objects.dates('fecha','year')
    year = request.GET.get('year','2014')
    municipio = request.GET.get('municipio','')
    periodo = Inversion.objects.filter(fecha__year=year).aggregate(max_fecha=Max('fecha'))['max_fecha']

    if municipio:
        source = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__fecha=periodo).values('catinversion').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('catinversion')
    else:
        source = Proyecto.objects.filter(inversion__fecha=periodo).values('catinversion').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('catinversion')

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
                  'stacking': False},
                'terms':{
                  'catinversion__nombre': [
                    'asignado']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Inversion asignados: %s %s' % (municipio, year,)},
              })

    ejecutado = Chart(
            datasource = oimdata,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'catinversion__nombre': [
                    'ejecutado']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Inversion ejecutados: %s %s' % (municipio, year,)},
              })

    return render_to_response('inversionpiechart.html',{'charts': (ejecutado, asignado, ), 'year_list': year_list, 'municipio_list': municipio_list})

def ogm_pie_chart(request):
    municipio_list = Municipio.objects.all()
    year_list = Gasto_year_list()
    year = request.GET.get('year','2014')
    municipio = request.GET.get('municipio','')
    periodo = Gasto.objects.filter(fecha__year=year).aggregate(max_fecha=Max('fecha'))['max_fecha']

    if municipio:
        source = GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__fecha=periodo).values('subsubtipogasto__origen').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('subsubtipogasto__origen')
    else:
        source = GastoDetalle.objects.filter(gasto__fecha=periodo).values('subsubtipogasto__origen').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('subsubtipogasto__origen')

    oimdata = DataPool(
           series=
            [{'options': {'source': source },
              'terms': [
                'subsubtipogasto__origen__nombre',
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
                  'subsubtipogasto__origen__nombre': [
                    'asignado']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Gastos asignados: %s %s' % (municipio, year,)},
              })

    ejecutado = Chart(
            datasource = oimdata,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False},
                'terms':{
                  'subsubtipogasto__origen__nombre': [
                    'ejecutado']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Gastos ejecutados: %s %s' % (municipio, year,)},
              })

    return render_to_response('ogmpiechart.html',{'charts': (ejecutado, asignado, ), 'year_list': year_list, 'municipio_list': municipio_list})

def oim_pie_chart(request):
    municipio_list = Municipio.objects.all()
    year_list = Ingreso_year_list()
    periodos = Ingreso_periodos()
    year = request.GET.get('year','2014')
    municipio = request.GET.get('municipio','')
    periodo = Ingreso.objects.filter(fecha__year=year).aggregate(max_fecha=Max('fecha'))['max_fecha']

    if municipio:
        source = IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio, ingreso__fecha=periodo).values('subsubtipoingreso__origen').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('subsubtipoingreso__origen')
        source_barra = IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio, ingreso__fecha__in=periodos)
    else:
        source = IngresoDetalle.objects.filter(ingreso__fecha=periodo).values('subsubtipoingreso__origen').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('subsubtipoingreso__origen')
        #source_barra = IngresoDetalle.objects.filter(ingreso__fecha__in=periodos).values('ingreso__fecha','subsubtipoingreso__origen').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('subsubtipoingreso__origen')
        source_barra = IngresoDetalle.objects.filter(ingreso__fecha__in=periodos)


    oimdata_barra = PivotDataPool(
           series=
            [{'options': {
                'source': source_barra,
                'categories': 'ingreso__fecha',
                'legend_by': 'subsubtipoingreso__origen__nombre',
                },
              'terms': {
                'sum_ejecutado':Sum('ejecutado'),
                #'sum_asignado':Sum('asignado'),
                }}
             ],
             sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
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

    asignado_barra = PivotChart(
            datasource = oimdata_barra,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': 'percent'},
                'terms':['sum_ejecutado']}],
            chart_options =
              {'title': {
                   'text': 'Ingresos asignados: %s %s' % (municipio, year,)},
              },
           )

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
              {'title': {
                   'text': 'Ingresos ejecutados: %s %s' % (municipio, year,)},
              })

    return render_to_response('oimpiechart.html',{'charts': (ejecutado, asignado, asignado_barra, ), 'year_list': year_list, 'municipio_list': municipio_list})

def oim_chart(slug):
    municipio_list = Municipio.objects.all()
    year_list = Ingreso.objects.all().dates('fecha','year').distinct()
    year = '2014'
    municipio = slug
    periodo = Ingreso.objects.filter(fecha__year=year).aggregate(max_fecha=Max('fecha'))['max_fecha']

    if municipio:
        source = IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio, ingreso__fecha=periodo).values('subsubtipoingreso__origen').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('subsubtipoingreso__origen')
        source_barra = IngresoDetalle.objects.all().values('ingreso__fecha','subsubtipoingreso__origen').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('subsubtipoingreso__origen')
    else:
        source = IngresoDetalle.objects.filter(ingreso__fecha=periodo).values('subsubtipoingreso__origen').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('subsubtipoingreso__origen')
        source_barra = IngresoDetalle.objects.all().values('ingreso__fecha','subsubtipoingreso__origen').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('subsubtipoingreso__origen')


    oimdata_barra = DataPool(
           series=
            [{'options': {'source': source_barra },
              'terms': [
                'ingreso__fecha',
                'subsubtipoingreso__origen__nombre',
                'ejecutado',
                'asignado',
                ]}
             ])
    oimdata = DataPool(
           series=
            [{'options': {'source': source },
              'terms': [
                'subsubtipoingreso__origen__nombre',
                'ejecutado',
                'asignado',
                ]}
             ])

    asignado_barra = Chart(
            datasource = oimdata_barra,
            series_options =
              [{'options':{
                  'type': 'column',
                  'stacking': 'percent'},
                'terms':{
                  'ingreso__fecha': [
                    'asignado']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Ingresos asignados: %s %s' % (municipio, year,)},
              })

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
              {'title': {
                   'text': 'Ingresos ejecutados: %s %s' % (municipio, year,)},
              })

    return {'charts': (ejecutado, asignado, ), 'year_list': year_list, 'municipio_list': municipio_list}
