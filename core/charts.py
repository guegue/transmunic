# -*- coding: utf-8 -*-

from itertools import chain
from datetime import datetime, time

from django.shortcuts import render_to_response
from django.db.models import Q, Sum, Max, Min, Avg

from chartit import DataPool, Chart, PivotDataPool, PivotChart, RawDataPool

from models import IngresoDetalle, Ingreso, GastoDetalle, Gasto, Inversion, Proyecto, Municipio, TipoGasto, InversionFuente, InversionFuenteDetalle, CatInversion, ClasificacionMunicAno
#from models import Gasto_year_list, Gasto_periodos, Ingreso_year_list, Ingreso_periodos, Inversion_year_list, Inversion_periodos, InversionFuente_year_list, InversionFuente_periodos
from models import getYears
from models import PERIODO_INICIAL, PERIODO_ACTUALIZADO, PERIODO_FINAL

def inversion_minima_sector_chart(municipio=None, year=None):
    municipio_list = Municipio.objects.all()
    year_list = getYears(Inversion)
    if not year:
        year = list(year_list)[-2]

    if municipio:
        source_ejecutado = Proyecto.objects.filter(inversion__year=year, inversion__periodo=PERIODO_FINAL, catinversion__minimo__gt=0, inversion__municipio__slug=municipio).values('catinversion__nombre').annotate(ejecutado=Sum('ejecutado'))
        source_asignado = Proyecto.objects.filter(inversion__year=year, inversion__periodo=PERIODO_INICIAL, catinversion__minimo__gt=0, inversion__municipio__slug=municipio).values('catinversion__nombre').annotate(asignado=Sum('asignado'))
        source = CatInversion.objects.filter(minimo__gt=0).values('nombre', 'minimo',)
        total_asignado = Proyecto.objects.filter(inversion__year=year_inicial, inversion__municipio__slug=municipio).aggregate(total=Sum('asignado'))
    else:
        municipio = ''
        source_ejecutado = Proyecto.objects.filter(inversion__year=year, inversion__periodo=PERIODO_FINAL, catinversion__minimo__gt=0).values('catinversion__nombre').annotate(ejecutado=Sum('ejecutado'))
        source_asignado = Proyecto.objects.filter(inversion__year=year, inversion__periodo=PERIODO_INICIAL, catinversion__minimo__gt=0).values('catinversion__nombre').annotate(asignado=Sum('asignado'))
        source = CatInversion.objects.filter(minimo__gt=0).values('nombre', 'minimo',)
        total_asignado = Proyecto.objects.filter(inversion__year=year, inversion__periodo=PERIODO_INICIAL).aggregate(total=Sum('asignado'))

    for record in source:
        record['ejecutado'] = 0 if not source_ejecutado else source_ejecutado.filter(catinversion__nombre=record['nombre'])[0]['ejecutado']
        record['asignado'] = 0 if not source_asignado else source_asignado.filter(catinversion__nombre=record['nombre'])[0]['asignado']
        record['minimo'] = 0 if not total_asignado['total'] else total_asignado['total'] * (record['minimo']/100)
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
    return {'charts': (chart,), 'year_list': year_list, 'municipio_list': municipio_list}



def fuentes_chart(municipio=None,year=None):
    municipio_list = Municipio.objects.all()
    year_list = InversionFuente.objects.distinct('year')
    if not year:
        year = list(year_list)[-1]
    if municipio:
        source = InversionFuenteDetalle.objects.filter(inversionfuente__municipio__slug=municipio, inversionfuente__year=year).\
                values('fuente').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('fuente__nombre')
    else:
        municipio = ''
        source = InversionFuenteDetalle.objects.filter(inversionfuente__year=year, inversionfuente__periodo=PERIODO_FINAL).\
                values('fuente').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('fuente__nombre')
        source_portada = InversionFuenteDetalle.objects.filter(inversionfuente__year=year, inversionfuente__periodo=PERIODO_FINAL).\
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
                  'text': 'Financiamiento de la inversión %s %s' % (municipio, year,)},
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
                  'text': 'Financiamiento de la inversión %s %s' % (municipio, year,)},
                  'plotOptions': { 'pie': { 'dataLabels': { 'enabled': False }, 'showInLegend': True, }},
              })
    return {'charts': (asignado, asignado_portada), 'year_list': year_list, 'municipio_list': municipio_list}

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


def inversion_area_chart(municipio=None):
    municipio_list = Municipio.objects.all()
    year_list = getYears(Inversion)

    if municipio:
        source = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__periodo=PERIODO_INICIAL)
        q = Q()
        for y in list(year_list)[-3:]:
            q |= Q(inversion__year=y)
        source_barra = Proyecto.objects.filter(q, inversion__municipio__slug=municipio, inversion__periodo=PERIODO_INICIAL)
    else:
        municipio = ''
        source = Proyecto.objects.filter(inversion__periodo=PERIODO_INICIAL)
        q = Q()
        for y in list(year_list)[-3:]:
            q |= Q(inversion__year=y)
        source_barra = Proyecto.objects.filter(q, inversion__periodo=PERIODO_INICIAL)

    data_barra = PivotDataPool(
           series=
            [{'options': {
                'source': source_barra,
                'categories': 'inversion__year',
                'legend_by': ['areageografica'],
                },
              'terms': {
                'sum_ejecutado':Sum('ejecutado'),
                'sum_asignado':Sum('asignado'),
                }}
             ],
             #sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
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
                'categories': 'inversion__year',
                'legend_by': ['areageografica'],
                },
              'terms': {
                'sum_ejecutado':Sum('ejecutado'),
                'sum_asignado':Sum('asignado'),
                }}
             ],
             #sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
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
    year_list = getYears(Ingreso)
    municipio = request.GET.get('municipio','')
    if municipio:
        with open ("core/ep_municipio.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [municipio, municipio, periodos])
    else:
        municipio = ''
        with open ("core/ep.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [year_list])
    data = RawDataPool(
           series=
            [{'options': {'source': source },
              'terms': [
                'year',
                'ejecutado',
                ]}
             ])

    bar = Chart(
            datasource = data,
            series_options =
              [{'options':{
                  'type': 'bar',},
                'terms':{
                  'year': [
                    'ejecutado']
                  }}],
            chart_options = {
                'title': {
                  'text': u'Ejecución del presupuesto %s ' % (municipio,)},
                },
            #x_sortf_mapf_mts = (None, lambda i:  i.strftime('%Y'), False)
            )

    return render_to_response('agochart.html',{'charts': (bar, ), 'municipio_list': municipio_list})

def psd_chart(request):
    municipio_list = Municipio.objects.all()
    year_list = getYears(Ingreso)[:-1]
    #periodos = list(Ingreso_periodos())[:-1]
    municipio = request.GET.get('municipio','')
    if municipio:
        with open ("core/psd_municipio.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [municipio, municipio, municipio, municipio, periodos])
    else:
        municipio = ''
        with open ("core/psd.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [year_list])
    data = RawDataPool(
           series=
            [{'options': {'source': source },
              'terms': [
                'year',
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
                  'year': [
                    'asignado',
                    'ejecutado']
                  }}],
            chart_options = {
                'title': {
                  'text': u'Peso del servicio de la deuda %s ' % (municipio,)},
                },
            #x_sortf_mapf_mts = (None, lambda i:  i.strftime('%Y'), False)
            )

    return render_to_response('agochart.html',{'charts': (bar, ), 'municipio_list': municipio_list})

def aci_chart(request):
    municipio_list = Municipio.objects.all()
    year_list = getYears(Ingreso)
    municipio = request.GET.get('municipio','')
    if municipio:
        with open ("core/aci_municipio.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [municipio, municipio, municipio, municipio, municipio, municipio, periodos])
    else:
        municipio = ''
        with open ("core/aci.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [year_list])
    data = RawDataPool(
           series=
            [{'options': {'source': source },
              'terms': [
                'year',
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
                  'year': [
                    'asignado',
                    'ejecutado']
                  }}],
            chart_options = {
                'title': {
                  'text': u'Ahorro corriente para inversiones %s ' % (municipio,)},
                },
            #x_sortf_mapf_mts = (None, lambda i:  i.strftime('%Y'), False)
            )

    return render_to_response('agochart.html',{'charts': (bar, ), 'municipio_list': municipio_list})


def ago_chart(request):
    municipio_list = Municipio.objects.all()
    year_list = getYears(Ingreso)[:-1]
    #periodos = list(Ingreso_periodos())[:-1]
    municipio = request.GET.get('municipio','')

    if municipio:
        with open ("core/ago_municipio.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [municipio, municipio, municipio, municipio, municipio, municipio, periodos])
    else:
        municipio = ''
        with open ("core/ago.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [year_list])

    data = RawDataPool(
           series=
            [{'options': {'source': source },
              'terms': [
                'year',
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
                  'year': [
                    'asignado',
                    'ejecutado']
                  }}],
            chart_options = {
                'title': {
                  'text': u'Autonomía %s ' % (municipio,)},
                },
                #x_sortf_mapf_mts = (None, lambda i:  i.strftime('%Y'), False)
            )

    return render_to_response('agochart.html',{'charts': (bar, ), 'municipio_list': municipio_list})

def gpersonal_chart(request):
    municipio_list = Municipio.objects.all()
    year_list = getYears(Gasto)
    municipio = request.GET.get('municipio','')
    year = request.GET.get('year', None)
    if not year:
        year = list(year_list)[-2]

    if municipio:
        source_barra = GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL, tipogasto=TipoGasto.PERSONAL)
        source_ejecutado = GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL, tipogasto=TipoGasto.PERSONAL).exclude(gasto__year=year)
    else:
        municipio = ''
        source_barra = GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL, tipogasto=TipoGasto.PERSONAL)
        source_ejecutado = GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL, tipogasto=TipoGasto.PERSONAL).exclude(gasto__year=year)

        # chart: porcentage gastos de personal
        source_pgp_asignado =  GastoDetalle.objects.filter(gasto__year=year, gasto__periodo=PERIODO_INICIAL, tipogasto=TipoGasto.PERSONAL).aggregate(asignado=Sum('asignado'))
        source_pgp_asignado['nombre'] = 'Personal'
        otros_asignado = GastoDetalle.objects.filter(gasto__year=year, gasto__periodo=PERIODO_INICIAL).exclude(tipogasto=TipoGasto.PERSONAL).aggregate(asignado=Sum('asignado'))
        otros_asignado['nombre'] = 'Otros'
        source_pgp = [source_pgp_asignado, otros_asignado]

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
                'categories': 'gasto__year',
                'legend_by': 'subtipogasto__nombre',
                },
              'terms': {
                'sum_ejecutado':Sum('ejecutado'),
                }}
             ],
             #sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
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
                'categories': 'gasto__year',
                'legend_by': 'subtipogasto__nombre',
                },
              'terms': {
                'sum_asignado':Sum('asignado'),
                }}
             ],
             #sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
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
    year_list = getYears(Gasto)
    year = request.GET.get('year', None)
    if not year:
        year = list(year_list)[-2]

    from collections import OrderedDict #FIXME move up
    if municipio:
        source_inicial = GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL, \
            tipogasto__clasificacion=TipoGasto.CORRIENTE, gasto__municipio__slug=municipio).\
            values('gasto__year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_final = GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL, \
            tipogasto__clasificacion=TipoGasto.CORRIENTE, gasto__municipio__slug=municipio).\
            values('gasto__year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        mi_gasto_promedio = GastoDetalle.objects.filter(tipogasto__clasificacion=TipoGasto.CORRIENTE, gasto__municipio__slug=municipio).aggregate(asignado=Sum('asignado'))['asignado']
        mi_clasificacion = ClasificacionMunicAno.objects.filter(desde__lt=mi_gasto_promedio, hasta__gt=mi_gasto_promedio)
        gasto_promedio = GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL, \
            tipogasto__clasificacion=TipoGasto.CORRIENTE, gasto__municipio__clasificacionmunicano=mi_clasificacion). \
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
            tipogasto__clasificacion=TipoGasto.CORRIENTE, gasto__municipio__slug=municipio).\
            values('gasto__year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_barra_final = source_barra # FIXME este es un work-around

        # chart: porcentage gastos de funcionamiento
        source_pgf_asignado =  GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL, tipogasto__clasificacion=TipoGasto.CORRIENTE).aggregate(asignado=Sum('asignado'))
        source_pgf_asignado['nombre'] = 'Funcionamiento'
        otros_asignado = GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL).exclude(tipogasto__clasificacion=TipoGasto.CORRIENTE).aggregate(asignado=Sum('asignado'))
        otros_asignado['nombre'] = 'Otros'
        source_pgf = [source_pgf_asignado, otros_asignado]
    else:
        municipio = ''
        source_inicial = GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL, \
            tipogasto__clasificacion=TipoGasto.CORRIENTE).\
            values('gasto__year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_final = GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL, \
            tipogasto__clasificacion=TipoGasto.CORRIENTE).\
            values('gasto__year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        try:
            for record in source_inicial:
                record['ejecutado'] = source_final.filter(gasto__year=record['gasto__year'])[0]['ejecutado']
        except IndexError:
            pass
        source = source_inicial

        # FIXME. en el grafico de periodos...  de donde tomar los datos?
        source_barra_inicial = GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL, \
            tipogasto__clasificacion=TipoGasto.CORRIENTE).\
            values('gasto__year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
        source_barra_final = GastoDetalle.objects.filter(gasto__periodo=PERIODO_FINAL, \
            tipogasto__clasificacion=TipoGasto.CORRIENTE).\
            values('gasto__year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

        # chart: porcentage gastos de funcionamiento
        source_pgf_asignado =  GastoDetalle.objects.filter(gasto__year=year, gasto__periodo=PERIODO_INICIAL, tipogasto__clasificacion=TipoGasto.CORRIENTE).aggregate(asignado=Sum('asignado'))
        source_pgf_asignado['nombre'] = 'Funcionamiento'
        otros_asignado = GastoDetalle.objects.filter(gasto__year=year, gasto__periodo=PERIODO_INICIAL).exclude(tipogasto__clasificacion=TipoGasto.CORRIENTE).aggregate(asignado=Sum('asignado'))
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
                'title': {'text': 'Gastos de funcionamiento %s ' % (municipio,)},
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
            chart_options = {'title': {'text': u'Gastos de funcionamiento año %s ' % (municipio,)}},
            #x_sortf_mapf_mts = (None, lambda i:  i.strftime('%Y'), False)
            )

    return render_to_response('gfchart.html',{'charts': (gfbar, barra, pie), 'municipio_list': municipio_list})


def inversion_categoria_chart(request):
    municipio_list = Municipio.objects.all()
    year_list = getYears(Inversion)
    year = list(year_list)[-1]
    municipio = request.GET.get('municipio','')

    if municipio:
        source = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__year=year).values('catinversion__nombre').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('catinversion')
        source_ultimos = Proyecto.objects.filter(inversion__municipio__slug=municipio, inversion__year__gt=list(year_list)[-3]). \
            values('inversion__year').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))
    else:
        municipio = ''
        source = Proyecto.objects.filter(inversion__year=year).values('catinversion__nombre').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('catinversion')
        source_ultimos = Proyecto.objects.filter(inversion__year__gt=list(year_list)[-3]). \
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

    # tabla: get total and percent
    total = source.aggregate(total=Sum('asignado'))['total']
    for row in source:
        row['percent'] = round(row['asignado'] / total * 100, 0)

    # tabla: get ingresos por año
    porano_table = {}
    ys = source_ultimos.order_by('catinversion__nombre').values('catinversion__nombre').distinct()
    for y in ys:
        label = y['catinversion__nombre']
        porano_table[label] = {}
        for ayear in year_list:
            value = source_ultimos.filter(inversion__year=ayear, catinversion__nombre=label).aggregate(total=Sum('asignado'))['total']
            porano_table[label][ayear] = value if value else ''
        if municipio and year:
            value = IngresoDetalle.objects.filter(ingreso__year=year, subsubtipoingreso__origen__nombre=label, ingreso__municipio__clasificacionmunic=mi_clasificacion).aggregate(total=Sum('asignado'))['total']

    mi_clasificacion = None

    return render_to_response('inversionpiechart.html',{'charts': (ejecutado, asignado, ultimos), \
        'clasificacion': mi_clasificacion, 'ano': year, 'porano': porano_table, 'totales': source, \
        'year_list': year_list, 'municipio_list': municipio_list})

def ogm_chart(municipio=None, year=None):
    municipio_list = Municipio.objects.all()
    year_list = getYears(Gasto)
    if not year:
        year = list(year_list)[-1]

    if municipio:
        source = GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__year=year).values('tipogasto__nombre').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('tipogasto__nombre')
        q = Q()
        for y in list(year_list)[-3:]:
            q |= Q(gasto__year=y)
        source_barra = GastoDetalle.objects.filter(q, gasto__municipio__slug=municipio)
        source_pivot = GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL, gasto__municipio__slug=municipio)
        mi_clasificacion = ClasificacionMunicAno.objects.get(municipio__slug=municipio, year=year)
    else:
        municipio = ''
        mi_clasificacion = None
        source = GastoDetalle.objects.filter(gasto__year=year).values('tipogasto__nombre').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('tipogasto__nombre')
        q = Q()
        for y in list(year_list)[-3:]:
            q |= Q(gasto__year=y)
        source_barra = GastoDetalle.objects.filter(q)
        source_pivot = GastoDetalle.objects.filter(gasto__periodo=PERIODO_INICIAL)


    pivot_barra = PivotDataPool(
           series=
            [{'options': {'source': source_pivot,
                        'categories': 'gasto__year',
                        'legend_by': 'tipogasto__nombre', },
              'terms': {
                  'ejecutado':Sum('ejecutado'),
                  'asignado':Sum('asignado'),
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
                'terms':['asignado']
                }],
            chart_options =
              {'title': { 'text': 'Gastos asignados por tipo %s' % (municipio,)}},
            )
    ogmdata_barra = PivotDataPool(
           series=
            [{'options': {'source': source_barra,
                        'categories': 'gasto__year',
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
                  'text': 'Destino de los gastos %s %s' % (municipio, year,)},
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

    # tabla: get total and percent
    total = source.aggregate(total=Sum('asignado'))['total']
    for row in source:
        row['percent'] = round(row['asignado'] / total * 100, 0)

    # tabla: get ingresos por año
    porano_table = {}
    ys = source_barra.order_by('tipogasto__nombre').values('tipogasto__nombre').distinct()
    for y in ys:
        label = y['tipogasto__nombre']
        porano_table[label] = {}
        for ayear in year_list:
            value = source_barra.filter(gasto__year=ayear, tipogasto__nombre=label).aggregate(total=Sum('asignado'))['total']
            porano_table[label][ayear] = value if value else ''
        if municipio and year:
            value = IngresoDetalle.objects.filter(ingreso__year=year, subsubtipoingreso__origen__nombre=label, ingreso__municipio__clasificacionmunicano=mi_clasificacion).aggregate(total=Sum('asignado'))['total']

    return {'charts': (ejecutado, asignado, asignado_barra, barra), 'clasificacion': mi_clasificacion, 'ano': year, 'porano': porano_table, 'totales': source, 'year_list': year_list, 'municipio_list': municipio_list}

def oim_chart(municipio=None, year=None):
    municipio_list = Municipio.objects.all()
    year_list = getYears(Ingreso)
    if not year:
        year = list(year_list)[-1]

    if municipio:
        source = IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio, ingreso__year=year).values('subsubtipoingreso__origen__nombre').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('subsubtipoingreso__origen')
        source_barra = IngresoDetalle.objects.filter(ingreso__periodo=PERIODO_INICIAL, ingreso__municipio__slug=municipio)
        q = Q()
        for y in list(year_list)[-3:]:
            q |= Q(ingreso__year=y)
        source_barra2 = IngresoDetalle.objects.filter(q, ingreso__municipio__slug=municipio)
        mi_clasificacion = ClasificacionMunicAno.objects.get(municipio__slug=municipio, anio=year)
    else:
        mi_clasificacion = None
        municipio = ''
        source = IngresoDetalle.objects.filter(ingreso__periodo=PERIODO_INICIAL).values('subsubtipoingreso__origen__nombre').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('subsubtipoingreso__origen')
        source_barra = IngresoDetalle.objects.filter(ingreso__periodo=PERIODO_INICIAL)
        source_barra2 = IngresoDetalle.objects.filter(ingreso__year__gt=list(year_list)[-3])

    oimdata_barra = PivotDataPool(
           series=
            [{'options': {'source': source_barra,
                        'categories': 'ingreso__year',
                        'legend_by': 'subsubtipoingreso__origen__nombre', },
              'terms': {
                  'ejecutado':Sum('ejecutado'),
                  'asignado':Sum('asignado'),
                }
              }],
            #sortf_mapf_mts = (None, lambda i:  (datetime.strptime(i[0], '%Y-%m-%d').strftime('%Y'),), False)
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
                        'categories': 'ingreso__year',
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
                  'text': 'Origen de los ingresos %s %s' % (municipio, year,)},
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

    # tabla: get total and percent
    total = source.aggregate(total=Sum('asignado'))['total']
    for row in source:
        row['percent'] = round(row['asignado'] / total * 100, 0)

    # tabla: get ingresos por año
    porano_table = {}
    ys = source_barra.order_by('subsubtipoingreso__origen__nombre').values('subsubtipoingreso__origen__nombre').distinct()
    for y in ys:
        label = y['subsubtipoingreso__origen__nombre']
        porano_table[label] = {}
        for ayear in year_list:
            value = source_barra.filter(ingreso__year=ayear, subsubtipoingreso__origen__nombre=label).aggregate(total=Sum('asignado'))['total']
            porano_table[label][ayear] = value if value else ''
        if municipio and year:
            value = IngresoDetalle.objects.filter(ingreso__year=year, subsubtipoingreso__origen__nombre=label, \
                    ingreso__municipio__clasificaciones__clasificacion=mi_clasificacion.clasificacion, ingreso__municipio__clase__anio=year).\
                    aggregate(total=Avg('asignado'))['total']
            porano_table[label]['extra'] = value if value else '...'

    return {'charts': (ejecutado, asignado, asignado_barra, barra2), 'clasificacion': mi_clasificacion, 'ano': year, 'porano': porano_table, 'totales': source, 'year_list': year_list, 'municipio_list': municipio_list}
