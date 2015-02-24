# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.db.models import Sum, Max

from chartit import DataPool, Chart

from models import IngresoDetalle, Ingreso, Municipio

def oim_pie_chart(request):
    municipio_list = Municipio.objects.all()
    year_list = Ingreso.objects.all().dates('fecha','year').distinct()
    year = request.GET.get('year','2014')
    municipio = request.GET.get('municipio','')
    periodo = Ingreso.objects.filter(fecha__year=year).aggregate(max_fecha=Max('fecha'))['max_fecha']

    if municipio:
        #source = IngresoDetalle.objects.filter(ingreso__municipio__nombre=u'%s' % (municipio,), ingreso__fecha=periodo).values('subsubtipoingreso__origen').annotate(ejecutado=Sum('ejecutado')).order_by('subsubtipoingreso__origen')
        source = IngresoDetalle.objects.filter(ingreso__municipio__slug=municipio, ingreso__fecha=periodo).values('subsubtipoingreso__origen').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('subsubtipoingreso__origen')
    else:
        source = IngresoDetalle.objects.filter(ingreso__fecha=periodo).values('subsubtipoingreso__origen').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado')).order_by('subsubtipoingreso__origen')

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
                       'text': 'Origen de ingreso'})

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
                       'text': 'Origen de ingreso'})

    return render_to_response('oimpiechart.html',{'pies': (ejecutado, asignado, ), 'year_list': year_list, 'municipio_list': municipio_list})
