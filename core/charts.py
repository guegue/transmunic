from django.shortcuts import render_to_response
from django.db.models import Sum, Max

from chartit import DataPool, Chart

from models import IngresoDetalle, Ingreso

def oim_pie_chart(request):
    year = request.GET.get('year')
    periodo = Ingreso.objects.filter(fecha__year=year).aggregate(max_fecha=Max('fecha'))['max_fecha']
    oimdata = \
        DataPool(
           series=
            [{'options': {
               'source': IngresoDetalle.objects.filter(ingreso__fecha=periodo).values('subsubtipoingreso__origen').annotate(ejecutado=Sum('ejecutado')).order_by('subsubtipoingreso__origen')},
              'terms': [
                'subsubtipoingreso__origen__nombre',
                'ejecutado']}
             ])

    cht = Chart(
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
                   'text': 'Ingresos'},
                       'text': 'Origen de ingreso'})

    return render_to_response('oimpiechart.html',{'oimpiechart': cht})
