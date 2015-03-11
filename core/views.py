from django.shortcuts import render
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.views.generic.detail import DetailView
from django.db.models import Sum, Max

from models import Municipio, Inversion, Inversion_year_list, Proyecto
from charts import oim_chart, ogm_chart, inversion_chart, inversion_area_chart
from website.models import Banner

# Create your views here.
def home(request):
    template_name = 'index.html'
    banners = Banner.objects.all()

    year_list = Inversion_year_list()
    year = list(year_list)[-1].year

    data_oim = oim_chart(year=year)
    data_ogm = ogm_chart(year=year)
    data_inversion = inversion_chart()
    data_inversion_area = inversion_area_chart()

    periodo = Inversion.objects.filter(fecha__year=year).aggregate(max_fecha=Max('fecha'))['max_fecha']
    total_inversion = Proyecto.objects.filter(inversion__fecha=periodo). \
            aggregate(ejecutado=Sum('ejecutado'))
    inversion_categoria = Proyecto.objects.filter(inversion__fecha=periodo, ). \
            values('catinversion__slug','catinversion__nombre').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

    return render_to_response(template_name, { 'banners': banners,
        'charts':( data_oim['charts'][1], data_ogm['charts'][1], data_inversion['charts'][0], data_inversion_area['charts'][0]),
        'inversion_categoria': inversion_categoria,
        'total_inversion': total_inversion,
    })

def municipio(request, slug):
    obj = get_object_or_404(Municipio, slug=slug)
    template_name = 'municipio.html'

    banners = Banner.objects.filter(municipio__slug=slug)

    year_list = Inversion_year_list()
    year = list(year_list)[-1].year

    data_oim = oim_chart(municipio=slug, year=year)
    data_ogm = ogm_chart(municipio=slug, year=year)
    data_inversion = inversion_chart(municipio=slug)
    data_inversion_area = inversion_area_chart(municipio=slug)

    periodo = Inversion.objects.filter(fecha__year=year).aggregate(max_fecha=Max('fecha'))['max_fecha']
    total_inversion = Proyecto.objects.filter(inversion__fecha=periodo, inversion__municipio__slug=slug). \
            aggregate(ejecutado=Sum('ejecutado'))
    inversion_categoria = Proyecto.objects.filter(inversion__fecha=periodo, inversion__municipio__slug=slug). \
            values('catinversion__slug','catinversion__nombre').annotate(ejecutado=Sum('ejecutado'), asignado=Sum('asignado'))

    return render_to_response(template_name, { 'obj': obj, 'banners': banners,
        'charts':( data_oim['charts'][1], data_ogm['charts'][1], data_inversion['charts'][0], data_inversion_area['charts'][0]),
        'inversion_categoria': inversion_categoria,
        'total_inversion': total_inversion,
    })

def ogm_view(request):
    template_name = 'ogm_chart.html'
    municipio = request.GET.get('municipio','')
    year = request.GET.get('year','')
    data = ogm_chart(municipio=municipio, year=year)
    return render_to_response(template_name, { 'charts': data['charts'], 'year_list': data['year_list'], 'municipio_list': data['municipio_list']})

def oim_view(request):
    template_name = 'oim_chart.html'
    municipio = request.GET.get('municipio','')
    year = request.GET.get('year','')
    data = oim_chart(municipio=municipio, year=year)
    return render_to_response(template_name, { 'charts': data['charts'], 'year_list': data['year_list'], 'municipio_list': data['municipio_list']})

def inversion_view(request):
    template_name = 'inversion.html'
    municipio = request.GET.get('municipio','')
    data = inversion_chart(municipio=municipio)
    return render_to_response(template_name, {'charts': data['charts'], 'municipio_list': data['municipio_list']})

def inversion_area_view(request):
    template_name = 'inversionarea.html'
    municipio = request.GET.get('municipio','')
    data = inversion_area_chart(municipio=municipio)
    return render_to_response(template_name,{'charts': data['charts'], 'municipio_list': data['municipio_list']})
