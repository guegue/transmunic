# -*- coding: utf-8 -*-

from itertools import chain
from datetime import datetime, time

from django.db import connection
from django.db.models import Q, Sum, Max, Min, Avg, Count
from django.shortcuts import render_to_response
from django.template import RequestContext

from chartit import DataPool, Chart, PivotDataPool, PivotChart, RawDataPool

from core.models import Anio, IngresoDetalle, Ingreso, GastoDetalle, Gasto, Inversion, Proyecto, Municipio, TipoGasto, InversionFuente, InversionFuenteDetalle, CatInversion, ClasificacionMunicAno
from core.models import PERIODO_INICIAL, PERIODO_ACTUALIZADO, PERIODO_FINAL, PERIODO_VERBOSE
from core.tools import getYears, dictfetchall, glue

def getVar(var, request):
    foo = None
    if var in request.session:
        foo = request.session[var]
    if var in request.GET:
        foo = request.GET[var]
    request.session[var] = foo
    return foo

def inversion_minima_porclase(year, portada=False):

    periodo = Anio.objects.get(anio=year).periodo

    # usar 'asignado' para todo periodo si estamos en portada
    if portada:
        quesumar = 'asignado'
    else:
        quesumar = 'ejecutado'

    sql_tpl="SELECT clasificacion,minimo_inversion AS minimo,\
            ((SELECT SUM({quesumar}) FROM core_IngresoDetalle JOIN core_Ingreso ON core_IngresoDetalle.ingreso_id=core_Ingreso.id JOIN core_TipoIngreso ON core_IngresoDetalle.tipoingreso_id=core_TipoIngreso.codigo \
            JOIN lugar_clasificacionmunicano ON core_Ingreso.municipio_id=lugar_clasificacionmunicano.municipio_id AND core_Ingreso.anio=lugar_clasificacionmunicano.anio \
            WHERE core_Ingreso.anio={year} AND core_Ingreso.periodo='{periodo}' AND core_tipoingreso.clasificacion={clasificacion} AND  tipoingreso_id<>'{tipoingreso}' AND lugar_clasificacionmunicano.clasificacion_id=clase.id) -\
            (SELECT SUM({quesumar}) FROM core_GastoDetalle JOIN core_Gasto ON core_GastoDetalle.gasto_id=core_Gasto.id JOIN core_TipoGasto ON core_GastoDetalle.tipogasto_id=core_TipoGasto.codigo \
            JOIN lugar_clasificacionmunicano ON core_Gasto.municipio_id=lugar_clasificacionmunicano.municipio_id AND core_Gasto.anio=lugar_clasificacionmunicano.anio \
            WHERE core_Gasto.anio={year} AND core_Gasto.periodo='{periodo}' AND core_tipogasto.clasificacion={clasificacion} AND lugar_clasificacionmunicano.clasificacion_id=clase.id)) /\
            (SELECT SUM({quesumar}) FROM core_IngresoDetalle JOIN core_Ingreso ON core_IngresoDetalle.ingreso_id=core_Ingreso.id JOIN core_TipoIngreso ON core_IngresoDetalle.tipoingreso_id=core_TipoIngreso.codigo \
            JOIN lugar_clasificacionmunicano ON core_Ingreso.municipio_id=lugar_clasificacionmunicano.municipio_id AND core_Ingreso.anio=lugar_clasificacionmunicano.anio \
            WHERE core_Ingreso.anio={year} AND core_Ingreso.periodo='{periodo}' AND core_tipoingreso.clasificacion={clasificacion} AND  tipoingreso_id<>'{tipoingreso}' AND lugar_clasificacionmunicano.clasificacion_id=clase.id) * 100\
            AS {quesumar_as} FROM lugar_clasificacionmunic AS clase WHERE minimo_inversion>0"
    #sql = sql_tpl.format(quesumar=quesumar, year=year, periodo=PERIODO_FINAL, clasificacion='0', tipoingreso='FIXME15000000', quesumar_as='ejecutado')
    #cursor = connection.cursor()
    #cursor.execute(sql)
    #final = dictfetchall(cursor)
    #sql = sql_tpl.format(quesumar='asignado', year=year, periodo=PERIODO_INICIAL, clasificacion='0', tipoingreso='FIXME15000000', quesumar_as='asignado')
    sql = sql_tpl.format(quesumar='asignado', year=year, periodo=periodo, clasificacion='0', tipoingreso='FIXME15000000', quesumar_as='asignado')
    cursor = connection.cursor()
    cursor.execute(sql)
    inicial = dictfetchall(cursor)
    #porclase = glue(inicial, final, 'clasificacion')
    data = RawDataPool(
           series=
            #[{'options': {'source': porclase },
            [{'options': {'source': inicial },
              'names': [u'Categorías de municipios', u'Mínimo por ley', u'Presupuestado'],
              'terms': [
                  'clasificacion',
                  'minimo',
                  #'ejecutado',
                  'asignado',
                ]}
             ])

    chart = Chart(
            datasource = data,
            series_options =
              [{'options':{ 'type': 'column', },
                  #'terms':{ 'clasificacion': [ 'asignado', 'ejecutado', 'minimo', ] }
                  'terms':{ 'clasificacion': [ 'asignado', 'minimo', ] }
              }],
            chart_options =
              {
                  #grafico 4 de portada
                  'title': {'text': u' '},
                  'tooltip': { 'pointFormat': '{series.name}: <b>{point.y:.2f}%</b>' },
              })
    return {'charts': (chart,), }

def inversion_minima_sector_chart(municipio=None, year=None, portada=False):
    municipio_list = Municipio.objects.all()
    year_list = getYears(Inversion)
    if not year:
        year = list(year_list)[-1]
    periodo = Anio.objects.get(anio=year).periodo

    # usar 'asignado' para todo periodo si estamos en portada
    if portada:
        quesumar = 'asignado'
    else:
        quesumar = 'ejecutado'

    if municipio:
        #source_ejecutado = Proyecto.objects.filter(inversion__anio=year, inversion__periodo=PERIODO_FINAL, catinversion__minimo__gt=0, inversion__municipio__slug=municipio).values('catinversion__nombre').annotate(ejecutado=Sum(quesumar))
        #source_asignado = Proyecto.objects.filter(inversion__anio=year, inversion__periodo=PERIODO_INICIAL, catinversion__minimo__gt=0, inversion__municipio__slug=municipio).values('catinversion__nombre').annotate(asignado=Sum('asignado'))
        source_asignado = Proyecto.objects.filter(inversion__anio=year, inversion__periodo=periodo, catinversion__minimo__gt=0, inversion__municipio__slug=municipio).values('catinversion__nombre').annotate(asignado=Sum('asignado'))
        source = CatInversion.objects.filter(minimo__gt=0).values('nombre', 'minimo',)
        #total_asignado = Proyecto.objects.filter(inversion__anio=year, inversion__municipio__slug=municipio).aggregate(total=Sum('asignado'))['total']
        total_asignado = Proyecto.objects.filter(inversion__anio=year, inversion__periodo=periodo, inversion__municipio__slug=municipio).aggregate(total=Sum('asignado'))['total']
    else:
        municipio = ''
        #source_ejecutado = Proyecto.objects.filter(inversion__anio=year, inversion__periodo=PERIODO_FINAL, catinversion__minimo__gt=0).values('catinversion__nombre').annotate(ejecutado=Sum(quesumar))
        #source_asignado = Proyecto.objects.filter(inversion__anio=year, inversion__periodo=PERIODO_INICIAL, catinversion__minimo__gt=0).values('catinversion__nombre').annotate(asignado=Sum('asignado'))
        source_asignado = Proyecto.objects.filter(inversion__anio=year, inversion__periodo=periodo, catinversion__minimo__gt=0).values('catinversion__nombre').annotate(asignado=Sum('asignado'))
        source = CatInversion.objects.filter(minimo__gt=0).values('nombre', 'minimo',)
        #total_asignado = Proyecto.objects.filter(inversion__anio=year, inversion__periodo=PERIODO_INICIAL).aggregate(total=Sum('asignado'))['total'] / 100
        total_asignado = Proyecto.objects.filter(inversion__anio=year, inversion__periodo=periodo).aggregate(total=Sum('asignado'))['total'] / 100

    for record in source:
        #try:
        #    record['ejecutado'] = 0 if not source_ejecutado else source_ejecutado.filter(catinversion__nombre=record['nombre'])[0][quesumar] / total_asignado
        #except IndexError:
        #    record['ejecutado'] = 0
        try:
            record['asignado'] = 0 if not source_asignado else source_asignado.filter(catinversion__nombre=record['nombre'])[0][quesumar] / total_asignado
        except IndexError:
            record['asignado'] = 0
        #record['minimo'] = 0 if not total_asignado['total'] else total_asignado['total'] * (record['minimo']/100)
    data = RawDataPool(
           series=
            [{'options': {'source': source },
              #'names': [u'Sector priorizado', u'Mínimo por ley', u'Ejecutado', u'Presupuestado'],
              #'terms': ['nombre','minimo','ejecutado','asignado']
              'names': [u'Sector priorizado', u'Mínimo por ley', u'Presupuestado'],
              'terms': ['nombre', 'minimo', 'asignado']
                }
             ])

    chart = Chart(
            datasource = data,
            series_options =
              [{'options':{ 'type': 'column', },
                  #'terms':{ 'nombre': [ 'asignado', 'ejecutado', 'minimo', ] },
                  'terms':{ 'nombre': [ 'asignado', 'minimo', ] },
                  #'terms':{ 'nombre': [ {'asignado': {'name':'Test', 'legendIndex': '1'} }, 'ejecutado', 'minimo', ] },
              }],
            chart_options =
              {
                  #grafico 5 de portada Arto 12
                  'title': {'text': u' '},
                  'tooltip': { 'pointFormat': '{series.name}: <b>{point.y:.2f}%</b>' },
              })
    return {'charts': (chart,), 'year_list': year_list, 'municipio_list': municipio_list}



def fuentes_chart(municipio=None, year=None, portada=False):
    municipio_list = Municipio.objects.all()
    year_list = getYears(InversionFuente)
    periodo = Anio.objects.get(anio=year).periodo

    # usar 'asignado' para todo periodo si estamos en portada
    if portada:
        quesumar = 'asignado'
    else:
        quesumar = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'

    if not year:
        year = year_list[-1]
    if municipio:
        source = InversionFuenteDetalle.objects.filter(inversionfuente__municipio__slug=municipio, inversionfuente__anio=year, inversionfuente__periodo=periodo).\
                values('fuente').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('fuente__nombre')
        source_portada = InversionFuenteDetalle.objects.filter(inversionfuente__municipio__slug=municipio, inversionfuente__anio=year, inversionfuente__periodo=periodo).\
                values('fuente__tipofuente__nombre').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('fuente__tipofuente__nombre')
    else:
        municipio = ''
        source = InversionFuenteDetalle.objects.filter(inversionfuente__anio=year, inversionfuente__periodo=periodo).\
                values('fuente').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('fuente__nombre')
        source_portada = InversionFuenteDetalle.objects.filter(inversionfuente__anio=year, inversionfuente__periodo=periodo).\
                values('fuente__tipofuente__nombre').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('fuente__tipofuente__nombre')

    data = DataPool(series = [{'options': {'source': source }, 'terms': ['fuente__nombre', 'ejecutado', 'asignado', ]}])
    data_portada = DataPool(series = [{'options': {'source': source_portada }, 'terms': ['fuente__tipofuente__nombre', 'ejecutado', 'asignado', ]}])
    asignado = Chart(
            datasource = data,
            series_options =
              [{'options':{'type': 'pie'},
                'terms':{'fuente__nombre': [quesumar]}
              }],
            chart_options = {
                'title': {'text': u' '},
                'plotOptions': { 'pie': { 'dataLabels': { 'enabled': True, 'format': '{point.percentage:.1f} %' }, 'showInLegend': True, 'depth': 35}},
                'options3d': { 'enabled': 'true',  'alpha': '45', 'beta': '0' },
                'tooltip': { 'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>' },
            }
    )
    asignado_portada = Chart(
            datasource = data_portada,
            series_options =
              [{'options':{'type': 'pie'},
                'terms':{'fuente__tipofuente__nombre': [quesumar]}
              }],
            chart_options = {
                'title': {'text': u' '},
                'plotOptions': { 'pie': { 'dataLabels': { 'enabled': True, 'format': '{point.percentage:.1f} %' }, 'showInLegend': True, 'depth': 35}},
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
            q |= Q(inversion__anio=y)
        source_barra = Proyecto.objects.filter(q, inversion__municipio__slug=municipio, inversion__periodo=PERIODO_INICIAL)
    else:
        municipio = ''
        source = Proyecto.objects.filter(inversion__periodo=PERIODO_INICIAL)
        q = Q()
        for y in list(year_list)[-3:]:
            q |= Q(inversion__anio=y)
        source_barra = Proyecto.objects.filter(q, inversion__periodo=PERIODO_INICIAL)

    data_barra = PivotDataPool(
           series=
            [{'options': {
                'source': source_barra,
                'categories': 'inversion__anio',
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
                'categories': 'inversion__anio',
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
        with open ("core/charts/ep_municipio.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [municipio, municipio, year_list])
    else:
        municipio = ''
        with open ("core/charts/ep.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [year_list])
    data = RawDataPool(
           series=
            [{'options': {'source': source },
              'terms': [
                'anio',
                'ejecutado',
                ]}
             ])

    bar = Chart(
            datasource = data,
            series_options =
              [{'options':{
                  'type': 'bar',},
                'terms':{
                  'anio': [
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
        with open ("core/charts/psd_municipio.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [municipio, municipio, municipio, municipio, year_list])
    else:
        municipio = ''
        with open ("core/charts/psd.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [year_list])
    data = RawDataPool(
           series=
            [{'options': {'source': source },
              'terms': [
                'anio',
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
                  'anio': [
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
        with open ("core/charts/aci_municipio.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [municipio, municipio, municipio, municipio, municipio, municipio, year_list])
    else:
        municipio = ''
        with open ("core/charts/aci.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [year_list])
    data = RawDataPool(
           series=
            [{'options': {'source': source },
              'terms': [
                'anio',
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
                  'anio': [
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
                'plotOptions': { 'pie': { 'dataLabels': { 'enabled': True, 'format': '{point.percentage:.1f} %' }, 'showInLegend': True, 'depth': 35}},
                'tooltip': { 'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>' },
            },
    )
    data_ejecutado = PivotDataPool(
           series=
            [{'options': {
                'source': source_ejecutado,
                'categories': 'gasto__anio',
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
                'categories': 'gasto__anio',
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
