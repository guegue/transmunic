# -*- coding: utf-8 -*-

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

def inversion_minima_porclase(year):
    sql_tpl="SELECT clasificacion,minimo_inversion AS minimo,\
    (SELECT SUM(%s) FROM core_InversionFuenteDetalle JOIN core_InversionFuente on core_InversionFuenteDetalle.inversionfuente_id=core_InversionFuente.id JOIN lugar_clasificacionmunicano ON core_InversionFuente.municipio_id=lugar_clasificacionmunicano.municipio_id AND core_InversionFuente.year=lugar_clasificacionmunicano.anio \
    WHERE core_InversionFuente.year=%s AND tipofuente_id=%s AND lugar_clasificacionmunicano.clasificacion_id=clase.id AND core_InversionFuente.periodo='%s') /\
    (SELECT SUM(%s) FROM core_IngresoDetalle JOIN core_Ingreso on core_IngresoDetalle.ingreso_id=core_Ingreso.id \
    JOIN lugar_clasificacionmunicano ON core_Ingreso.municipio_id=lugar_clasificacionmunicano.municipio_id AND core_Ingreso.year=lugar_clasificacionmunicano.anio \
    WHERE %s > 0 AND core_Ingreso.year=%s AND core_Ingreso.periodo='%s' AND (tipoingreso_id='1000000' OR subtipoingreso_id='12010000') AND lugar_clasificacionmunicano.clasificacion_id=clase.id) * 100\
    AS %s FROM lugar_clasificacionmunic AS clase WHERE minimo_inversion>0"
    sql = sql_tpl % ('ejecutado', year, 2, PERIODO_FINAL, 'ejecutado', 'ejecutado', year, PERIODO_FINAL, 'ejecutado')
    print sql
    cursor = connection.cursor()
    cursor.execute(sql)
    final = dictfetchall(cursor)
    sql = sql_tpl % ('asignado', year, 2, PERIODO_INICIAL, 'asignado', 'asignado', year, PERIODO_INICIAL, 'asignado')
    cursor = connection.cursor()
    cursor.execute(sql)
    inicial = dictfetchall(cursor)
    porclase = glue(inicial, final, PERIODO_INICIAL, 'clasificacion')
    data = RawDataPool(
           series=
            [{'options': {'source': porclase },
              'terms': [
                'clasificacion',
                'minimo',
                'ejecutado',
                'asignado',
                ]}
             ])

    chart = Chart(
            datasource = data,
            series_options =
              [{'options':{ 'type': 'column', },
                'terms':{ 'clasificacion': [ 'asignado', 'ejecutado', 'minimo', ] }
              }],
            chart_options =
              {
                  'title': {'text': u'Inversion mínima por clase %s' % (year,)},
                  'tooltip': { 'pointFormat': '{series.name}: <b>{point.y:.2f}%</b>' },
              })
    return {'charts': (chart,), }

def inversion_minima_sector_chart(municipio=None, year=None):
    municipio_list = Municipio.objects.all()
    year_list = getYears(Inversion)
    if not year:
        year = list(year_list)[-1]

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
        total_asignado = Proyecto.objects.filter(inversion__year=year, inversion__periodo=PERIODO_INICIAL).aggregate(total=Sum('asignado'))['total'] / 100

    for record in source:
        try:
            record['ejecutado'] = 0 if not source_ejecutado else source_ejecutado.filter(catinversion__nombre=record['nombre'])[0]['ejecutado'] / total_asignado
        except IndexError:
            record['ejecutado'] = 0
        try:
            record['asignado'] = 0 if not source_asignado else source_asignado.filter(catinversion__nombre=record['nombre'])[0]['asignado'] / total_asignado
        except IndexError:
            record['asignado'] = 0
        #record['minimo'] = 0 if not total_asignado['total'] else total_asignado['total'] * (record['minimo']/100)
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
              {
                  'title': {'text': u'Gasto mínimo por sector %s %s' % (municipio, year,)},
                  'tooltip': { 'pointFormat': '{series.name}: <b>{point.y:.2f}%</b>' },
              })
    return {'charts': (chart,), 'year_list': year_list, 'municipio_list': municipio_list}



def fuentes_chart(municipio=None,year=None):
    municipio_list = Municipio.objects.all()
    year_list = getYears(InversionFuente)
    if not year:
        year = year_list[-1]
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
            chart_options = {
                'title': {'text': 'Financiamiento de la inversión %s %s' % (municipio, year,)},
                'plotOptions': { 'pie': { 'dataLabels': { 'enabled': False }, 'showInLegend': True, 'depth': 35}},
                'options3d': { 'enabled': 'true',  'alpha': '45', 'beta': '0' },
                'tooltip': { 'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>' },
            }
    )
    asignado_portada = Chart(
            datasource = data_portada,
            series_options =
              [{'options':{'type': 'pie'},
                'terms':{'fuente__tipofuente__nombre': ['asignado']}
              }],
            chart_options = {
                'title': {'text': 'Financiamiento de la inversión %s' % (municipio, )},
                'plotOptions': { 'pie': { 'dataLabels': { 'enabled': False }, 'showInLegend': True, 'depth': 35}},
                'options3d': { 'enabled': 'true',  'alpha': '45', 'beta': '0' },
                'tooltip': { 'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>' },
              })
    return {'charts': (asignado, asignado_portada), 'year_list': year_list, 'municipio_list': municipio_list}


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
        source = IngresoDetalle.objects.raw(sql, [municipio, municipio, year_list])
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

    return render_to_response('agochart.html',{'charts': (bar, ), 'municipio_list': municipio_list},\
        context_instance=RequestContext(request))

def psd_chart(request):
    municipio_list = Municipio.objects.all()
    year_list = getYears(Ingreso)[:-1]
    municipio = request.GET.get('municipio','')
    if municipio:
        with open ("core/psd_municipio.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [municipio, municipio, municipio, municipio, year_list])
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

    return render_to_response('agochart.html',{'charts': (bar, ), 'municipio_list': municipio_list},\
        context_instance=RequestContext(request))

def aci_chart(request):
    municipio_list = Municipio.objects.all()
    year_list = getYears(Ingreso)
    municipio = request.GET.get('municipio','')
    if municipio:
        with open ("core/aci_municipio.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [municipio, municipio, municipio, municipio, municipio, municipio, year_list])
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


    return render_to_response('agochart.html',{'charts': (bar, ), 'municipio_list': municipio_list},\
        context_instance=RequestContext(request))


def ago_chart(request):
    municipio_list = Municipio.objects.all()
    year_list = getYears(Ingreso)[:-1]
    municipio = request.GET.get('municipio','')

    if municipio:
        with open ("core/ago_municipio.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [municipio, municipio, municipio, municipio, municipio, municipio, year_list])
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

    return render_to_response('agochart.html',{'charts': (bar, ), 'municipio_list': municipio_list},\
        context_instance=RequestContext(request))

def old_gpersonal_chart(request):
    municipio_list = Municipio.objects.all()
    year_list = getYears(Gasto)
    municipio = request.GET.get('municipio','')
    year = request.GET.get('year', None)
    if not year:
        year = list(year_list)[-2]

    if municipio:
        source_barra = GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL, tipogasto=TipoGasto.PERSONAL)
        source_ejecutado = GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__periodo=PERIODO_INICIAL, tipogasto=TipoGasto.PERSONAL).exclude(gasto__year=year)
        
        # chart: porcentage gastos de personal
        source_pgp_asignado =  GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__year=year, gasto__periodo=PERIODO_INICIAL, tipogasto=TipoGasto.PERSONAL).aggregate(asignado=Sum('asignado'))
        source_pgp_asignado['nombre'] = 'Personal'
        otros_asignado = GastoDetalle.objects.filter(gasto__municipio__slug=municipio, gasto__year=year, gasto__periodo=PERIODO_INICIAL).exclude(tipogasto=TipoGasto.PERSONAL).aggregate(asignado=Sum('asignado'))
        otros_asignado['nombre'] = 'Otros'
        source_pgp = [source_pgp_asignado, otros_asignado]

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
                'options3d': { 'enabled': 'true',  'alpha': '45', 'beta': '0' },
                'plotOptions': { 'pie': { 'dataLabels': { 'enabled': False }, 'showInLegend': True, 'depth': 35}},
                'tooltip': { 'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>' },
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
    return render_to_response('gpersonal.html',{'charts': (chart, chart_ejecutado, pie), 'municipio_list': municipio_list, 'year_list': year_list},\
        context_instance=RequestContext(request))
