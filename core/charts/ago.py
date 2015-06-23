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

def ago_chart(request):
    municipio_list = Municipio.objects.all()
    year_list = getYears(Ingreso)[:-1]
    municipio = request.GET.get('municipio','')

    if municipio:
        with open ("core/charts/ago_municipio.sql", "r") as query_file:
            sql=query_file.read()
        source = IngresoDetalle.objects.raw(sql, [municipio, municipio, municipio, municipio, municipio, municipio, year_list])
    else:
        municipio = ''
        with open ("core/charts/ago.sql", "r") as query_file:
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
                  'text': u'Autonomía %s ' % (municipio,)},
                },
                #x_sortf_mapf_mts = (None, lambda i:  i.strftime('%Y'), False)
            )

    return render_to_response('agochart.html',{'charts': (bar, ), 'municipio_list': municipio_list},\
        context_instance=RequestContext(request))
