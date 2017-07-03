# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.views.generic.detail import DetailView
from django.db.models import Sum, Max

from models import Anio, Departamento, Municipio, Inversion, Proyecto, InversionFuente, Grafico, CatInversion
from models import PERIODO_INICIAL, PERIODO_ACTUALIZADO, PERIODO_FINAL, PERIODO_VERBOSE, AREAGEOGRAFICA_VERBOSE
from tools import getYears
from charts.misc import fuentes_chart, inversion_minima_sector_chart, inversion_area_chart, inversion_minima_porclase, getVar
from charts.inversion import inversion_chart, inversion_categoria_chart
from charts.oim import oim_chart
from charts.ogm import ogm_chart
from charts.bubble_oim import oim_bubble_chart_data
from charts.bubble_ogm import ogm_bubble_chart_data
from website.models import Banner
from core.forms import DetallePresupuestoForm
import json

# Create your views here.
def home(request):
    template_name = 'home.html'
    banners = Banner.objects.all()

    #cleans session vars
    request.session['year'] = None
    request.session['municipio'] = None

    #descripcion de graficos de portada
    desc_oim_chart = Grafico.objects.get(pk='oim_ejecutado')
    desc_ogm_chart = Grafico.objects.get(pk='ogm_ejecutado')
    desc_invfuentes_chart = Grafico.objects.get(pk='fuentes')
    desc_inversionminima = Grafico.objects.get(pk='inversiones')
    desc_inversionsector = Grafico.objects.get(pk='inversion')
    #fin de descripcion de graficos de portada
    # consulta sobre consulta presupuestaria muelle de los bueyes
    desc_consultamb = Grafico.objects.get(pk='consultamb')

    departamentos = Departamento.objects.all()
    categorias = CatInversion.objects.filter(destacar=True)
    otras_categorias = CatInversion.objects.filter(destacar=False)

    # InversionFuente tiene su propio último año
    year_list = getYears(InversionFuente)
    year = year_list[-1]
    data_fuentes = fuentes_chart(year=year, portada=True)

    # obtiene último año
    year_list = getYears(Inversion)
    year = year_list[-1]

    # obtiene periodo del año a ver
    periodo = Anio.objects.get(anio=year).periodo

    # siempre sumar 'asginado'
    #quesumar = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'
    quesumar = 'asignado'

    data_oim = oim_chart(year=year, portada=True)
    data_ogm = ogm_chart(year=year, portada=True)

    #FIXME no 'quesumar'? usa asignado y ejecutado
    #data_inversion = inversion_chart()
    #FIXME no 'quesumar'? solo usa ejecutado
    #data_inversion_area = inversion_area_chart()

    data_inversion_minima_sector = inversion_minima_sector_chart(portada=True)
    data_inversion_minima_porclase = inversion_minima_porclase(year, portada=True)

    total_inversion = Proyecto.objects.filter(inversion__anio=year, inversion__periodo=periodo).aggregate(ejecutado=Sum(quesumar))
    inversion_categoria = Proyecto.objects.filter(inversion__anio=year, inversion__periodo=periodo, catinversion__destacar=True). \
            values('catinversion__slug','catinversion__minimo','catinversion__nombre',).annotate(ejecutado=Sum(quesumar))
    inversion_categoria2 = Proyecto.objects.filter(inversion__anio=year, inversion__periodo=periodo, catinversion__destacar=False). \
            values('catinversion__slug','catinversion__minimo','catinversion__nombre','catinversion__id').annotate(ejecutado=Sum(quesumar))
    return render_to_response(template_name, { 'banners': banners,'desc_oim_chart':desc_oim_chart,'desc_ogm_chart':desc_ogm_chart, 'desc_invfuentes_chart':desc_invfuentes_chart,'desc_inversionminima':desc_inversionminima,'desc_inversionsector':desc_inversionsector,'desc_consultamb':desc_consultamb,
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
        'inversion_categoria2': inversion_categoria2,
        'total_inversion': total_inversion,
        'departamentos': departamentos,
        'categorias': categorias,
        'otras_categorias': otras_categorias,
        'totales_oim': data_oim['totales'],
        'totales_ogm': data_ogm['totales'],
        'rubros': data_oim['rubros'],
        'data_oim': data_oim,
        'data_ogm': data_ogm,
        'home': 'home',
        'year': year,
        'periodo': periodo,
    }, context_instance=RequestContext(request))

def municipio(request, slug=None, year=None):
    template_name = 'consolidado_municipal.html'
    if slug is not None:
        obj = get_object_or_404(Municipio, slug=slug)
        municipio = get_object_or_404(Municipio, slug=slug)
    else:
        obj = None
    year = request.GET.get('year','2015')
    #banners = Banner.objects.filter(municipio__slug=slug)
    banners = Banner.objects.all()
    #descripcion de graficos de portada
    desc_oim_chart = Grafico.objects.get(pk='oim_ejecutado')
    desc_ogm_chart = Grafico.objects.get(pk='ogm_ejecutado')
    desc_invfuentes_chart = Grafico.objects.get(pk='fuentes')
    desc_inversionminima = Grafico.objects.get(pk='inversiones')
    desc_inversionsector = Grafico.objects.get(pk='inversion')
    #fin de descripcion de graficos de portada
    departamentos = Departamento.objects.all()
    categorias = CatInversion.objects.filter(destacar=True)
    otras_categorias = CatInversion.objects.filter(destacar=False)

    # InversionFuente tiene su propio último año
    year_list = getYears(InversionFuente)

    data_fuentes = fuentes_chart(year=year, municipio=slug, portada=True)

    # obtiene periodo del año a ver
    periodo = Anio.objects.get(anio=year).periodo

    # siempre sumar 'asginado'
    #quesumar = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'
    quesumar = 'asignado'

    if slug is not None:
        data_oim = oim_chart(year=year, municipio=slug, portada=True)
        data_ogm = ogm_chart(year=year, municipio=slug, portada=True)
        bubble_oim = oim_bubble_chart_data(municipio=slug, year=year)
        data_inversion_minima_sector = inversion_minima_sector_chart(municipio=slug, portada=True)
    else:
        data_oim = oim_chart( year=year, municipio=slug, portada=True)
        data_ogm = ogm_chart( year=year, municipio=slug, portada=True)
        bubble_oim = oim_bubble_chart_data( year=year)
        data_inversion_minima_sector = inversion_minima_sector_chart(year=year, municipio=slug, portada=True)

    data_inversion_minima_porclase = inversion_minima_porclase(year, portada=True)

    total_inversion = Proyecto.objects.filter(inversion__municipio__slug=slug, inversion__periodo=periodo, inversion__anio=year).aggregate(ejecutado=Sum(quesumar))

    inversion_categoria = Proyecto.objects.filter(inversion__anio=year, inversion__periodo=periodo). \
            values('catinversion__slug','catinversion__minimo','catinversion__nombre',).annotate(ejecutado=Sum(quesumar))
    inversion_categoria2 = Proyecto.objects.filter(inversion__anio=year, inversion__periodo=periodo, catinversion__destacar=True). \
            values('catinversion__slug','catinversion__minimo','catinversion__nombre','catinversion__id').annotate(ejecutado=Sum(quesumar))
    return render_to_response(template_name, { 
        'banners': banners,
        'desc_oim_chart':desc_oim_chart,
        'desc_ogm_chart':desc_ogm_chart,
        'desc_invfuentes_chart':desc_invfuentes_chart,
        'desc_inversionminima':desc_inversionminima,
        'desc_inversionsector':desc_inversionsector,
        'charts':(
            data_oim['charts'][0],
            data_ogm['charts'][0],
            #data_inversion['charts'][0],
            data_inversion_minima_sector['charts'][0],
            #data_inversion_area['charts'][0],
            data_inversion_minima_porclase['charts'][0],
            data_fuentes['charts'][1],
            ),
        'mi_clase': data_oim['mi_clase'],
        'bubble_data': bubble_oim,
        'inversion_categoria': inversion_categoria,
        'inversion_categoria2': inversion_categoria2,
        'categorias': categorias,
        'otras_categorias': otras_categorias,
        'total_inversion': total_inversion,
        'totales_ogm': data_ogm['totales'],
        'departamentos': departamentos,
        'municipio': obj,
        'year_list': data_oim['year_list'],
        'year': year,
        'periodo': periodo,
        'home': 'home',
        'data_oim': data_oim,
        'data_ogm': data_ogm,
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
    indicator_name = "Inversión municipal"

    # InversionFuente tiene su propio último año
    year_list = getYears(InversionFuente)
    year = year_list[-1]
    data_fuentes = fuentes_chart(year=year)
    data['charts'].append( fuentes_chart(year=year)['charts'][1] )

    bubble_data = {'label':"Total", 'amount': round(data['asignado']/1000000, 2)}
    child_l1 = []
    for child in data['cat']:
        child_data = {'color':  child['catinversion__color'], 'name': child['catinversion__id'], 'label':child['catinversion__nombre'], 'amount': round(child['asignado']/1000000, 2)}
        child_l1.append(child_data)
    bubble_data['children'] = child_l1
    bubble_source = json.dumps(bubble_data)

    reporte = request.POST.get("reporte","")
    if "excel" in request.POST.keys() and reporte:
        from core.utils import obtener_excel_response
        data = { \
            'municipio': data['municipio'], 'year': data['year'], 'mi_clase': data['mi_clase'], 'porano': data['porano'], \
            'cat': data['cat'], 'anuales': data['anuales'], 'porclasep': data['porclasep'], 'otros': data['otros'], \
            'totales': data['totales'], 'charts': data['charts'], 'year_list': data['year_list'], 'municipio_list': data['municipio_list'], \
            'asignado': data['asignado'], 'ejecutado': data['ejecutado']}
        return obtener_excel_response(reporte=reporte, data=data)

    return render_to_response(template_name, { \
            'indicator_name': indicator_name, \
            'municipio': data['municipio'], 'year': data['year'], 'mi_clase': data['mi_clase'], 'porano': data['porano'], \
            'cat': data['cat'], 'anuales': data['anuales'], 'porclasep': data['porclasep'], 'otros': data['otros'], \
            'totales': data['totales'], 'charts': data['charts'], 'year_list': data['year_list'], 'municipio_list': data['municipio_list'], \
            'asignado': data['asignado'], 'ejecutado': data['ejecutado'], 'bubble_data': bubble_source}, \
            context_instance=RequestContext(request))

def ogm_view(request):
    template_name = 'ogm_chart.html'
    municipio = getVar('municipio', request)
    year = getVar('year', request)
    data = ogm_chart(municipio=municipio, year=year)
    indicator_name = "Destino de los gastos"
    bubble_data = ogm_bubble_chart_data(municipio=municipio, year=year)
    reporte = request.POST.get("reporte","")
    if "excel" in request.POST.keys() and reporte:
        from core.utils import obtener_excel_response
        return obtener_excel_response(reporte=reporte, data=data)

    return render_to_response(template_name, { \
            'indicator_name': indicator_name, \
            'year_data': data['year_data'], \
            'municipio': data['municipio'], 'year': data['year'], 'mi_clase': data['mi_clase'], 'porano': data['porano'], \
            'totales': data['totales'], 'charts': data['charts'], 'year_list': data['year_list'], 'municipio_list': data['municipio_list'], \
            'porclase': data['porclase'], 'porclasep': data['porclasep'], 'rubros': data['rubros'], 'anuales': data['anuales'],\
            'rubrosp': data['rubrosp'], 'otros': data['otros'],\
            'asignado': data['asignado'], 'ejecutado': data['ejecutado'], 'bubble_data': bubble_data}, \
            context_instance=RequestContext(request))

def oim_view(request):
    template_name = 'oim_chart.html'
    municipio = getVar('municipio', request)
    year = getVar('year', request)
    indicator_name = "Origen de los ingresos"
    data = oim_chart(municipio=municipio, year=year)
    bubble_data = oim_bubble_chart_data(municipio=municipio, year=year)
    reporte = request.POST.get("reporte","")
    if "excel" in request.POST.keys() and reporte:
        from core.utils import obtener_excel_response
        return obtener_excel_response(reporte=reporte, data=data)

    return render_to_response(template_name, { \
            'indicator_name': indicator_name, \
            'year_data': data['year_data'], \
            'municipio': data['municipio'], 'year': data['year'], 'mi_clase': data['mi_clase'], 'porano': data['porano'], \
            'totales': data['totales'], 'charts': data['charts'], 'periodo_list': data['periodo_list'], 'year_list': data['year_list'], 'municipio_list': data['municipio_list'], \
            'porclase': data['porclase'], 'porclasep': data['porclasep'], 'rubros': data['rubros'], 'anuales': data['anuales'],\
            'rubrosp': data['rubrosp'], 'otros': data['otros'],\
            'asignado': data['asignado'], 'ejecutado': data['ejecutado'], 'bubble_data': bubble_data}, \
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
            'municipio': municipio, 'periodo_list': data['periodo_list'],},\
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
