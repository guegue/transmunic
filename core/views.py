# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.views.generic.detail import DetailView
from django.db.models import Sum, Max

from models import Departamento, Municipio, Inversion, Proyecto, InversionFuente, Grafico
from models import Anio, getYears
from models import PERIODO_INICIAL, PERIODO_ACTUALIZADO, PERIODO_FINAL, PERIODO_VERBOSE, AREAGEOGRAFICA_VERBOSE
from charts.misc import fuentes_chart, inversion_minima_sector_chart, inversion_area_chart, inversion_minima_porclase, getVar
from charts.inversion import inversion_chart, inversion_categoria_chart
from charts.oim import oim_chart
from charts.ogm import ogm_chart
from website.models import Banner
from core.forms import DetallePresupuestoForm

# Create your views here.
def home(request):
    template_name = 'index.html'
    banners = Banner.objects.all()
    #descripcion de graficos de portada 
    desc_oim_chart = Grafico.objects.get(pk='oim_ejecutado')
    desc_ogm_chart = Grafico.objects.get(pk='ogm_ejecutado')
    desc_invfuentes_chart = Grafico.objects.get(pk='fuentes')
    desc_inversionminima = Grafico.objects.get(pk='inversiones')
    desc_inversionisector = Grafico.objects.get(pk='inversion')
    #fin de descripcion de graficos de portada
    departamentos = Departamento.objects.all()

    # InversionFuente tiene su propio último año
    year_list = getYears(InversionFuente)
    year = year_list[-1]
    data_fuentes = fuentes_chart(year=year)

    year_list = getYears(Inversion)
    year = year_list[-1]
    periodo = Anio.objects.get(anio=year).periodo
    quesumar = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'

    data_oim = oim_chart(year=year, portada=True)
    data_ogm = ogm_chart(year=year)
    data_inversion = inversion_chart()
    data_inversion_area = inversion_area_chart()
    data_inversion_minima_sector = inversion_minima_sector_chart()
    data_inversion_minima_porclase = inversion_minima_porclase(year)

    total_inversion = Proyecto.objects.filter(inversion__anio=year).aggregate(ejecutado=Sum(quesumar))
    inversion_categoria = Proyecto.objects.filter(inversion__anio=year, ). \
            values('catinversion__slug','catinversion__minimo','catinversion__nombre').annotate(ejecutado=Sum(quesumar))

    return render_to_response(template_name, { 'banners': banners,'desc_oim_chart':desc_oim_chart,'desc_ogm_chart':desc_ogm_chart, 'desc_invfuentes_chart':desc_invfuentes_chart,'desc_inversionminima':desc_inversionminima,'desc_inversionisector':desc_inversionisector,
        'charts':( 
            data_oim['charts'][0], 
            data_ogm['charts'][0], 
            #data_inversion['charts'][0], 
            data_inversion_minima_sector['charts'][0],
            #data_inversion_area['charts'][0],
            data_inversion_minima_porclase['charts'][0],
            data_fuentes['charts'][1],
            ),
        'inversion_categoria': inversion_categoria,
        'total_inversion': total_inversion,
        'departamentos': departamentos,
        'home': 'home',
    }, context_instance=RequestContext(request))

def municipio(request, slug):
    obj = get_object_or_404(Municipio, slug=slug)
    template_name = 'municipio.html'
    #banners = Banner.objects.filter(municipio__slug=slug)
    banners = Banner.objects.all()
    #descripcion de graficos de portada 
    desc_oim_chart = Grafico.objects.get(pk='oim_ejecutado')
    desc_ogm_chart = Grafico.objects.get(pk='ogm_ejecutado')
    desc_invfuentes_chart = Grafico.objects.get(pk='fuentes')
    desc_inversionminima = Grafico.objects.get(pk='inversiones')
    desc_inversionisector = Grafico.objects.get(pk='inversion')
    #fin de descripcion de graficos de portada
    departamentos = Departamento.objects.all()

    # InversionFuente tiene su propio último año
    year_list = getYears(InversionFuente)
    year = year_list[-1]
    data_fuentes = fuentes_chart(year=year)

    year_list = getYears(Inversion)
    year = year_list[-1]
    periodo = Anio.objects.get(anio=year).periodo
    quesumar = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'

    data_oim = oim_chart(year=year, municipio=slug, portada=True)
    data_ogm = ogm_chart(year=year, municipio=slug, )
    data_inversion = inversion_chart()
    data_inversion_area = inversion_area_chart()
    data_inversion_minima_sector = inversion_minima_sector_chart()
    data_inversion_minima_porclase = inversion_minima_porclase(year)

    total_inversion = Proyecto.objects.filter(inversion__anio=year).aggregate(ejecutado=Sum(quesumar))
    inversion_categoria = Proyecto.objects.filter(inversion__anio=year, ). \
            values('catinversion__slug','catinversion__minimo','catinversion__nombre').annotate(ejecutado=Sum(quesumar))

    return render_to_response(template_name, { 'banners': banners,'desc_oim_chart':desc_oim_chart,'desc_ogm_chart':desc_ogm_chart, 'desc_invfuentes_chart':desc_invfuentes_chart,'desc_inversionminima':desc_inversionminima,'desc_inversionisector':desc_inversionisector,
        'charts':( 
            data_oim['charts'][0], 
            data_ogm['charts'][0], 
            #data_inversion['charts'][0], 
            data_inversion_minima_sector['charts'][0],
            #data_inversion_area['charts'][0],
            data_inversion_minima_porclase['charts'][0],
            data_fuentes['charts'][1],
            ),
        'inversion_categoria': inversion_categoria,
        'total_inversion': total_inversion,
        'departamentos': departamentos,
        'home': 'home',
    }, context_instance=RequestContext(request))

def inversion_minima_sector_view(request):
    template_name = 'chart.html'
    municipio = request.GET.get('municipio','')
    year = request.GET.get('year','')
    data = inversion_minima_sector_chart(municipio=municipio, year=year)
    return render_to_response(template_name, {'charts': data['charts'], 'municipio_list': data['municipio_list'], 'year_list': data['year_list']},\
            context_instance=RequestContext(request))

def inversion_categoria_view(request):
    template_name = 'inversionpiechart.html'
    municipio = getVar('municipio', request)
    year = getVar('year', request)
    data = inversion_categoria_chart(municipio=municipio, year=year)

    # InversionFuente tiene su propio último año
    year_list = getYears(InversionFuente)
    year = year_list[-1]
    data_fuentes = fuentes_chart(year=year)
    data['charts'].append( fuentes_chart(year=year)['charts'][1] )

    reporte = request.POST.get("reporte","") 
    if "excel" in request.POST.keys() and reporte:        
        from core.utils import obtener_excel_response
        data = { \
            'municipio': data['municipio'], 'year': data['year'], 'mi_clase': data['mi_clase'], 'porano': data['porano'], \
            'cat': data['cat'], 'anuales': data['anuales'], 'porclasep': data['porclasep'], 'otros': data['otros'], \
            'totales': data['totales'], 'charts': data['charts'], 'year_list': data['year_list'], 'municipio_list': data['municipio_list'], \
            'year': year, \
            'asignado': data['asignado'], 'ejecutado': data['ejecutado']}          
        return obtener_excel_response(reporte=reporte, data=data)

    return render_to_response(template_name, { \
            'municipio': data['municipio'], 'year': data['year'], 'mi_clase': data['mi_clase'], 'porano': data['porano'], \
            'cat': data['cat'], 'anuales': data['anuales'], 'porclasep': data['porclasep'], 'otros': data['otros'], \
            'totales': data['totales'], 'charts': data['charts'], 'year_list': data['year_list'], 'municipio_list': data['municipio_list'], \
            'asignado': data['asignado'], 'ejecutado': data['ejecutado']}, \
            context_instance=RequestContext(request))

def ogm_view(request):
    template_name = 'ogm_chart.html'
    municipio = getVar('municipio', request)
    year = getVar('year', request)
    data = ogm_chart(municipio=municipio, year=year)
    reporte = request.POST.get("reporte","") 
    if "excel" in request.POST.keys() and reporte:        
        from core.utils import obtener_excel_response            
        return obtener_excel_response(reporte=reporte, data=data)
    
    return render_to_response(template_name, { \
            'municipio': data['municipio'], 'year': data['year'], 'mi_clase': data['mi_clase'], 'porano': data['porano'], \
            'totales': data['totales'], 'charts': data['charts'], 'year_list': data['year_list'], 'municipio_list': data['municipio_list'], \
            'year': year, 'porclase': data['porclase'], 'porclasep': data['porclasep'], 'rubros': data['rubros'], 'anuales': data['anuales'],\
            'rubrosp': data['rubrosp'], 'otros': data['otros'],\
            'asignado': data['asignado'], 'ejecutado': data['ejecutado']}, \
            context_instance=RequestContext(request))

def oim_view(request):
    template_name = 'oim_chart.html'
    municipio = getVar('municipio', request)
    year = getVar('year', request)
    data = oim_chart(municipio=municipio, year=year)
    
    reporte = request.POST.get("reporte","") 
    if "excel" in request.POST.keys() and reporte:        
        from core.utils import obtener_excel_response            
        return obtener_excel_response(reporte=reporte, data=data)
        
    return render_to_response(template_name, { \
            'municipio': data['municipio'], 'year': data['year'], 'mi_clase': data['mi_clase'], 'porano': data['porano'], \
            'totales': data['totales'], 'charts': data['charts'], 'year_list': data['year_list'], 'municipio_list': data['municipio_list'], \
            'year': year, 'porclase': data['porclase'], 'porclasep': data['porclasep'], 'rubros': data['rubros'], 'anuales': data['anuales'],\
            'rubrosp': data['rubrosp'], 'otros': data['otros'],\
            'asignado': data['asignado'], 'ejecutado': data['ejecutado']}, \
            context_instance=RequestContext(request))

def inversion_view(request):
    template_name = 'inversion.html'
    municipio = getVar('municipio', request)
    year = getVar('year', request)
    data = inversion_chart(municipio=municipio, year=year)
    return render_to_response(template_name, {'charts': data['charts'], 'municipio_list': data['municipio_list'],\
            'municipio': data['municipio'], 'year': data['year'], 'mi_clase': data['mi_clase'], 'porano': data['porano'], \
            'porclasep': data['porclasep']},\
            context_instance=RequestContext(request))

def inversion_area_view(request):
    template_name = 'inversionarea.html'
    municipio = request.GET.get('municipio','')
    data = inversion_area_chart(municipio=municipio)
    return render_to_response(template_name,{'charts': data['charts'], 'municipio_list': data['municipio_list'],\
            'municipio': municipio, },\
            context_instance=RequestContext(request))

def fuentes_view(request):
    template_name = 'fuentes_chart.html'
    municipio = request.GET.get('municipio','')
    year = request.GET.get('year','')
    data = fuentes_chart(municipio=municipio, year=year)
    return render_to_response(template_name, { 'charts': data['charts'], 'year_list': data['year_list'], 'municipio_list': data['municipio_list'],\
            'municipio': municipio, 'year': year,},\
            context_instance=RequestContext(request))


def descargar_detalle(request):  
    error = ""  
    if request.method == 'POST':
        form = DetallePresupuestoForm(request.POST)
        if form.is_valid():
            from core.utils import descargar_detalle_excel
            result = descargar_detalle_excel(form, request)
            if result is not None:
                return result
            else:
                error = "No existen datos disponibles"
    else:
        form = DetallePresupuestoForm()
        
    return render_to_response('descargar_detalle.html', 
                              {"form":form,
                               "error":error
                               }, 
                              context_instance=RequestContext(request)
                              )
    
