# -*- coding: utf-8 -*-
import json

from django.shortcuts import render_to_response, render
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.db.models import Sum, CharField, F, Value as V
from django.db.models.functions import Concat

from models import (Anio, AnioTransferencia, Departamento,
                    Municipio, Inversion, Proyecto,
                    InversionFuente, Grafico, CatInversion,
                    Transferencia, PERIODO_INICIAL, PERIODO_FINAL)
from lugar.models import ClasificacionMunicAno, Periodo, PeriodoMunic
from tools import getYears, getPeriods, xnumber, growthRate
from charts.misc import (fuentes_chart, inversion_minima_sector_chart,
                         inversion_area_chart, inversion_minima_porclase,
                         getVar)
from charts.inversion import inversion_chart, inversion_categoria_chart
from charts.oim import oim_chart
from charts.ogm import ogm_chart
from charts.bubble_oim import oim_bubble_chart_data
from charts.bubble_ogm import ogm_bubble_chart_data
from website.models import Banner
from core.forms import DetallePresupuestoForm


# Create your views here.
def home(request):
    template_name = 'home.html'
    banners = Banner.objects.all()

    # cleans session vars
    request.session['year'] = None
    request.session['municipio'] = None

    # descripcion de graficos de portada
    desc_oim_chart = Grafico.objects.get(pk='oim_ejecutado')
    desc_ogm_chart = Grafico.objects.get(pk='ogm_ejecutado')
    # desc_invfuentes_chart = Grafico.objects.get(pk='fuentes')
    desc_inversionminima = Grafico.objects.get(pk='inversiones')
    desc_inversionsector = Grafico.objects.get(pk='inversion')
    # fin de descripcion de graficos de portada
    # consulta sobre consulta presupuestaria muelle de los bueyes
    # desc_consultamb = Grafico.objects.get(pk='consultamb')

    departamentos = Departamento.objects.all()
    categorias = CatInversion.objects.filter(destacar=True)
    otras_categorias = CatInversion.objects.filter(destacar=False)

    # InversionFuente tiene su propio último año
    # year_list = getYears(InversionFuente)
    # year = year_list[-1]
    # data_fuentes = fuentes_chart(year=year, portada=True)

    # obtiene último año
    year_list = getYears(Anio)
    year = year_list[-1]

    # obtiene periodo del año a ver
    if year:
        periodo = Anio.objects.get(anio=year).periodo

    data_inversion_minima_sector = inversion_minima_sector_chart(portada=True)
    # siempre sumar 'asginado'
    quesumar = 'asignado' if periodo == 'I' else 'ejecutado'

    if year:
        data_oim = oim_chart(year=year, portada=True)
        data_ogm = ogm_chart(year=year, portada=True)

        data_inversion_minima_porclase = inversion_minima_porclase(year, portada=True)
        total_inversion = Proyecto.objects.filter(
            inversion__anio=year, inversion__periodo=periodo).aggregate(ejecutado=Sum(quesumar))
        inversiones_categoria = Proyecto.objects. \
            filter(inversion__anio=year,
                   inversion__periodo=periodo). \
            values('catinversion__slug', 'catinversion__minimo',
                   'catinversion__nombre', 'catinversion__id',
                   'catinversion__destacar'). \
            order_by('-catinversion__destacar',
                     '-{}'.format(quesumar)). \
            annotate(asignado=Sum('asignado'), ejecutado=Sum('ejecutado'))

    context = {'banners': banners, 'desc_oim_chart': desc_oim_chart, 'desc_ogm_chart': desc_ogm_chart,
               'desc_inversionminima': desc_inversionminima, 'desc_inversionsector': desc_inversionsector,
               'charts': (
                   data_oim['charts'][0],
                   data_ogm['charts'][0],
                   # data_inversion['charts'][0],
                   data_inversion_minima_sector['charts'][0],
                   # data_inversion_area['charts'][0],
                   data_inversion_minima_porclase['charts'][0],
                   # data_fuentes['charts'][1],
               ),
               'inversion_categoria': inversiones_categoria,
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
               }
    return render(request, template_name, context)


def municipio(request, slug=None, year=None):
    template_name = 'consolidado_municipal.html'
    if slug is not None:
        obj = get_object_or_404(Municipio, slug=slug)
        municipio = get_object_or_404(Municipio, slug=slug)
    else:
        obj = None

    year_list = getYears(Anio)
    ''  # si el parametro year no existe se asigna el ultimo
    ''  # año registrado en la base de datos
    year = request.GET.get('year', year_list[-1])
    # banners = Banner.objects.filter(municipio__slug=slug)
    banners = Banner.objects.all()
    # descripcion de graficos de portada
    desc_oim_chart = Grafico.objects.get(pk='oim_ejecutado')
    desc_ogm_chart = Grafico.objects.get(pk='ogm_ejecutado')
    desc_invfuentes_chart = Grafico.objects.get(pk='fuentes')
    desc_inversionminima = Grafico.objects.get(pk='inversiones')
    desc_inversionsector = Grafico.objects.get(pk='inversion')
    # fin de descripcion de graficos de portada
    departamentos = Departamento.objects.all()
    categorias = CatInversion.objects.filter(destacar=True)
    otras_categorias = CatInversion.objects.filter(destacar=False)

    # InversionFuente tiene su propio último año
    year_list = getYears(InversionFuente)
    # investyear = year_list[-1]
    investyear = year

    data_fuentes = fuentes_chart(year=year, municipio=slug, portada=True)

    # obtiene periodo del año a ver
    periodo = Anio.objects.get(anio=year).periodo

    # siempre sumar 'asginado'
    # quesumar = 'asignado' if periodo == PERIODO_INICIAL else 'ejecutado'
    quesumar = 'asignado'

    if slug is not None:
        data_oim = oim_chart(year=year, municipio=slug, portada=True)
        data_ogm = ogm_chart(year=year, municipio=slug, portada=True)
        bubble_oim = oim_bubble_chart_data(municipio=slug, year=year)
        data_inversion_minima_sector = inversion_minima_sector_chart(municipio=slug, portada=True)
    else:
        data_oim = oim_chart(year=year, portada=True)
        data_ogm = ogm_chart(year=year, portada=True)
        bubble_oim = oim_bubble_chart_data(year=year)
        data_inversion_minima_sector = inversion_minima_sector_chart(year=year, municipio=slug, portada=True)

    data_inversion_minima_porclase = inversion_minima_porclase(year, portada=True)

    if slug is not None:
        total_inversion = Proyecto.objects.filter(inversion__municipio__slug=slug, inversion__periodo=periodo,
                                                  inversion__anio=year).aggregate(ejecutado=Sum(quesumar))
        inversion_categoria = Proyecto.objects.filter(
            inversion__municipio__slug=slug,
            inversion__anio=investyear,
            inversion__periodo=periodo, catinversion__destacar=True) \
            .values(
            'catinversion__slug',
            'catinversion__minimo',
            'catinversion__nombre') \
            .order_by() \
            .annotate(ejecutado=Sum(quesumar))
        inversion_categoria2 = Proyecto.objects.filter(
            inversion__municipio__slug=slug,
            inversion__anio=investyear,
            inversion__periodo=periodo,
            catinversion__destacar=False) \
            .values(
            'catinversion__slug',
            'catinversion__minimo',
            'catinversion__nombre',
            'catinversion__id') \
            .order_by() \
            .annotate(ejecutado=Sum(quesumar))
    else:
        total_inversion = Proyecto.objects.filter(inversion__anio=year, inversion__periodo=periodo).aggregate(
            ejecutado=Sum(quesumar))
        inversion_categoria = Proyecto.objects.filter(
            inversion__anio=investyear,
            inversion__periodo=periodo, catinversion__destacar=True) \
            .values(
            'catinversion__slug',
            'catinversion__minimo',
            'catinversion__nombre') \
            .order_by() \
            .annotate(ejecutado=Sum(quesumar))
        inversion_categoria2 = Proyecto.objects.filter(
            inversion__anio=investyear,
            inversion__periodo=periodo,
            catinversion__destacar=False) \
            .values(
            'catinversion__slug',
            'catinversion__minimo',
            'catinversion__nombre',
            'catinversion__id') \
            .order_by() \
            .annotate(ejecutado=Sum(quesumar))

    context = {
        'banners': banners,
        'desc_oim_chart': desc_oim_chart,
        'desc_ogm_chart': desc_ogm_chart,
        'desc_invfuentes_chart': desc_invfuentes_chart,
        'desc_inversionminima': desc_inversionminima,
        'desc_inversionsector': desc_inversionsector,
        'charts': (
            data_oim['charts'][0],
            data_ogm['charts'][0],
            # data_inversion['charts'][0],
            data_inversion_minima_sector['charts'][0],
            # data_inversion_area['charts'][0],
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
        'periodo_list': data_oim['periodo_list'],
    }
    return render(request, template_name, context)


def inversion_minima_sector_view(request):
    template_name = 'chart.html'
    municipio = request.GET.get('municipio', '')
    year = request.GET.get('year', '')
    data = inversion_minima_sector_chart(municipio=municipio, year=year)

    return render_to_response(
        template_name,
        {
            'charts': data['charts'],
            'municipio_list': data['municipio_list'],
            'year_list': data['year_list']
        },
        context_instance=RequestContext(request))


def inversion_categoria_view(request):
    template_name = 'inversionpiechart.html'
    municipio = getVar('municipio', request)
    year = getVar('year', request)
    data = inversion_categoria_chart(municipio=municipio, year=year)
    indicator_name = "Inversión municipal"

    # InversionFuente tiene su propio último año
    periodo_list = getPeriods(Inversion)
    year_list = getYears(InversionFuente)
    year = year_list[-1]
    data_fuentes = fuentes_chart(year=year)
    data['charts'].append(data_fuentes['charts'][1])

    bubble_data = {
        'label': "Total",
        'amount': round(data['asignado'] / 1000000, 2)
    }
    child_l1 = []
    for child in data['cat']:

        label = child['catinversion__nombre']
        if child['catinversion__shortname']:
            label = child['catinversion__shortname']

        child_data = {
            'color': child['catinversion__color'],
            'name': child['catinversion__id'],
            'slug': child['catinversion__slug'],
            'label': label,
            'amount': round(child['asignado'] / 1000000, 2)
        }
        child_l1.append(child_data)
    bubble_data['children'] = child_l1
    bubble_source = json.dumps(bubble_data)

    reporte = request.POST.get("reporte", "")
    if "excel" in request.POST.keys() and reporte:
        from core.utils import obtener_excel_response
        data = {
            'municipio': data['municipio'],
            'year': data['year'],
            'mi_clase': data['mi_clase'],
            'porano': data['porano'],
            'cat': data['cat'],
            'anuales': data['anuales'],
            'porclasep': data['porclasep'],
            'otros': data['otros'],
            'totales': data['totales'],
            'charts': data['charts'],
            'year_list': data['year_list'],
            'municipio_list': data['municipio_list'],
            'asignado': data['asignado'],
            'ejecutado': data['ejecutado']}
        return obtener_excel_response(reporte=reporte, data=data)

    context = {
        'indicator_name': indicator_name,
        'municipio': data['municipio'],
        'year': data['year'],
        'mi_clase': data['mi_clase'],
        'porano': data['porano'],
        'cat': data['cat'],
        'anuales': data['anuales'],
        'porclasep': data['porclasep'],
        'otros': data['otros'],
        'totales': data['totales'],
        'charts': data['charts'],
        'year_list': data['year_list'],
        'periodo': data['periodo'],
        'periodo_list': periodo_list,
        'municipio_list': data['municipio_list'],
        'asignado': data['asignado'],
        'asignado_porcentaje': data['asignado_porcentaje'],
        'ejecutado': data['ejecutado'],
        'ejecutado_porcentaje': data['ejecutado_porcentaje'],
        'actualizado_porcentaje': data['actualizado_porcentaje'],
        'bubble_data': bubble_source,
        'bubble_data_nojson': bubble_data
    }
    return render(request, template_name, context)


def ogm_view(request):
    template_name = 'ogm_chart.html'
    municipio = getVar('municipio', request)
    year = getVar('year', request)
    data = ogm_chart(municipio=municipio, year=year)
    indicator_name = "Destino de los gastos"
    bubble_data = ogm_bubble_chart_data(municipio=municipio, year=year)
    reporte = request.POST.get("reporte", "")
    if "excel" in request.POST.keys() and reporte:
        from core.utils import obtener_excel_response
        return obtener_excel_response(reporte=reporte, data=data)

    context = {
        'indicator_name': indicator_name,
        'periodo_list': data['periodo_list'],
        'year_data': data['year_data'],
        'municipio': data['municipio'], 'year': data['year'], 'mi_clase': data['mi_clase'], 'porano': data['porano'],
        'totales': data['totales'], 'charts': data['charts'], 'year_list': data['year_list'],
        'municipio_list': data['municipio_list'],
        'porclase': data['porclase'], 'porclasep': data['porclasep'], 'rubros': data['rubros'],
        'anuales': data['anuales'],
        'rubrosp': data['rubrosp'], 'otros': data['otros'],
        'asignado': data['asignado'], 'ejecutado': data['ejecutado'], 'bubble_data': bubble_data,
    }
    return render(request, template_name, context)


def oim_view(request):
    template_name = 'oim_chart.html'
    municipio = getVar('municipio', request)
    year = getVar('year', request)
    indicator_name = "Origen de los ingresos"
    data = oim_chart(municipio=municipio, year=year)
    bubble_data = oim_bubble_chart_data(municipio=municipio, year=year)
    reporte = request.POST.get("reporte", "")
    if "excel" in request.POST.keys() and reporte:
        from core.utils import obtener_excel_response
        return obtener_excel_response(reporte=reporte, data=data)

    context = {
        'indicator_name': indicator_name,
        'year_data': data['year_data'],
        'indicator_description': """Son los ingresos que capta el sector
                        público para realizar sus actividades, es decir, es el dinero
                        percibido por el gobierno para financiar sus gastos públicos""",
        'municipio': data['municipio'],
        'year': data['year'],
        'mi_clase': data['mi_clase'],
        'porano': data['porano'],
        'totales': data['totales'],
        'charts': data['charts'],
        'periodo_list': data['periodo_list'],
        'year_list': data['year_list'],
        'municipio_list': data['municipio_list'],
        'porclase': data['porclase'],
        'porclasep': data['porclasep'],
        'rubros': data['rubros'],
        'anuales': data['anuales'],
        'rubrosp': data['rubrosp'],
        'otros': data['otros'],
        'asignado': data['asignado'],
        'ejecutado': data['ejecutado'],
        'asignado_porcentaje': data['asignado_porcentaje'],
        'actualizado_porcentaje': data['actualizado_porcentaje'],
        'ejecutado_porcentaje': data['ejecutado_porcentaje'],
        'total_asignado_ranking': data['total_asignado_ranking'],
        'total_asignado_ranking_porcentaje':
            data['total_asignado_ranking_porcentaje'],
        'total_ejecutado_ranking':
            data['total_ejecutado_ranking'],
        'total_ejecutado_ranking_porcenteje':
            data['total_ejecutado_ranking_porcenteje'],
        'bubble_data': bubble_data
    }
    return render(request, template_name, context)


def inversion_view(request):
    template_name = 'inversion.html'
    municipio = getVar('municipio', request)
    year = getVar('year', request)
    data = inversion_chart(municipio=municipio, year=year)
    return render_to_response(template_name, {'charts': data['charts'], 'municipio_list': data['municipio_list'],
                                              'municipio': data['municipio'], 'year': data['year'],
                                              'mi_clase': data['mi_clase'], 'porano': data['porano'],
                                              'porclasep': data['porclasep'], 'periodo_list': data['periodo_list']},
                              context_instance=RequestContext(request))


def inversion_area_view(request):
    template_name = 'inversionarea.html'
    municipio = request.GET.get('municipio', '')
    data = inversion_area_chart(municipio=municipio)
    return render_to_response(template_name, {'charts': data['charts'], 'municipio_list': data['municipio_list'],
                                              'municipio': municipio, 'periodo_list': data['periodo_list'], },
                              context_instance=RequestContext(request))


def fuentes_view(request):
    template_name = 'fuentes_chart.html'
    municipio = request.GET.get('municipio', '')
    year = request.GET.get('year', '')
    data = fuentes_chart(municipio=municipio, year=year)
    return render_to_response(template_name, {'charts': data['charts'], 'year_list': data['year_list'],
                                              'municipio_list': data['municipio_list'],
                                              'municipio': municipio, 'year': year, },
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
                              {"form": form,
                               "error": error
                               },
                              context_instance=RequestContext(request)
                              )


def getTransferenciasDetalle():
    context = {}
    # botiene anios y sus periodos
    # TODO: usar anio__periodo='I' en vez de esto (crear realacion FK)
    iniciales = AnioTransferencia.objects. \
        values_list('anio', flat=True). \
        filter(periodo=PERIODO_INICIAL)

    finales = AnioTransferencia.objects. \
        values_list('anio', flat=True). \
        filter(periodo=PERIODO_FINAL)

    inicial_filter = {
        'anio__in': iniciales,
        'periodo': PERIODO_INICIAL}
    final_filter = {
        'anio__in': finales,
        'periodo': PERIODO_FINAL}

    data_inicial = Transferencia.objects. \
        order_by('municipio__nombre', 'anio'). \
        values('municipio__id', 'municipio__nombre',
               'anio'). \
        filter(**inicial_filter). \
        annotate(corriente=Sum('corriente'),
                 capital=Sum('capital'))

    data_final = Transferencia.objects. \
        order_by('municipio__nombre', 'anio'). \
        values('municipio__id', 'municipio__nombre',
               'anio'). \
        filter(**final_filter). \
        annotate(corriente=Sum('corriente'),
                 capital=Sum('capital'))

    data_inicial = list(data_inicial)
    data_final = list(data_final)
    data = data_inicial + data_final

    for row in data:
        row['total'] = row['corriente'] + row['capital']

    asignaciones = ('corriente', 'capital', 'total')
    context['asignaciones'] = asignaciones

    years_list = sorted(list(iniciales) + list(finales))
    context['years'] = years_list

    data_by_years = {}
    for year in years_list:
        data_by_years[year] = {
            'corriente': sum([row['corriente'] for row in data if row['anio'] == year]),
            'capital': sum([row['capital'] for row in data if row['anio'] == year]),
        }

    context['data_by_years'] = data_by_years
    context['data'] = data

    return context


def getTransferencias(municipio=None):
    context = {}
    # botiene anios y sus periodos
    # TODO: usar anio__periodo='I' en vez de esto (crear realacion FK)
    iniciales = AnioTransferencia.objects. \
        values_list('anio', flat=True). \
        filter(periodo=PERIODO_INICIAL)
    finales = AnioTransferencia.objects. \
        values_list('anio', flat=True). \
        filter(periodo=PERIODO_FINAL)
    inicial_filter = {'anio__in': iniciales, 'periodo': PERIODO_INICIAL}
    final_filter = {'anio__in': finales, 'periodo': PERIODO_FINAL}

    if municipio:
        inicial_filter['municipio__slug'] = municipio
        final_filter['municipio__slug'] = municipio

    data_inicial = Transferencia.objects.order_by('municipio', 'anio').values('municipio', 'anio'). \
        filter(**inicial_filter).annotate(corriente=Sum('corriente'), capital=Sum('capital'))

    data_final = Transferencia.objects.order_by('municipio', 'anio').values('municipio', 'anio'). \
        filter(**final_filter).annotate(corriente=Sum('corriente'), capital=Sum('capital'))

    # adds 'clasificacion' for each row
    for row in data_inicial:
        row['clasificacion'] = ClasificacionMunicAno.objects. \
            values_list('clasificacion__clasificacion', flat=True). \
            filter(anio=row['anio'], municipio=row['municipio']).first()
    for row in data_final:
        row['clasificacion'] = ClasificacionMunicAno.objects. \
            values_list('clasificacion__clasificacion', flat=True). \
            filter(anio=row['anio'], municipio=row['municipio']).first()

    data_inicial = list(data_inicial)
    data_final = list(data_final)

    # llena con ceros años por si quedan vacios
    if not municipio:
        clasificaciones = ClasificacionMunicAno.objects.values_list('clasificacion__clasificacion',
                                                                    flat=True).distinct()
        for year in iniciales:
            for clasificacion in clasificaciones:
                data_inicial.append({'anio': year, 'clasificacion': clasificacion, 'corriente': 0,
                                     'municipio': 0, 'capital': 0})
        for year in finales:
            for clasificacion in clasificaciones:
                data_final.append({'anio': year, 'clasificacion': clasificacion, 'corriente': 0,
                                   'municipio': 0, 'capital': 0})

    data = data_inicial + data_final

    for row in data:
        row['total'] = row['corriente'] + row['capital']

    asignaciones = ('corriente', 'capital', 'total')
    context['asignaciones'] = asignaciones

    if municipio:
        data = sorted(data, key=lambda k: (k['anio']))
        years = []
        periodos = {}
        for year in list(iniciales) + list(finales):
            clasificacion = ClasificacionMunicAno.objects. \
                values_list('clasificacion__clasificacion', flat=True). \
                filter(anio=year, municipio__slug=municipio).first()
            partido = PeriodoMunic.objects.values('partido', 'periodo__desde',
                                                  'periodo__hasta').filter(
                municipio__slug=municipio, periodo__desde__lte=year,
                periodo__hasta__gte=year).first()
            periodo = "{}-{}".format(partido['periodo__desde'], partido['periodo__hasta'])
            periodos[periodo] = periodos.get(periodo, 0) + 1
            years.append({'year': year, 'clasificacion': clasificacion,
                          'partido': partido['partido'], 'periodo': periodo})
        for year in years:
            year['span'] = periodos[year['periodo']]

        # re-arrange data
        data_asignacion = {}
        for asignacion in asignaciones:
            data_asignacion[asignacion] = []
        for row in data:
            for asignacion in asignaciones:
                data_asignacion[asignacion].append(row[asignacion])

        context['municipio'] = Municipio.objects.get(slug=municipio)
        context['data_asignacion'] = data_asignacion
        sorted_years = sorted(years, key=lambda x: x['year'])
        context['years'] = sorted_years

    if not municipio:
        # group by clasificacion
        data_sum = {}
        for row in data:
            a_key = "{}_{}".format(row['clasificacion'], row['anio'])
            if not data_sum.get(a_key):
                data_sum[a_key] = {'corriente': 0, 'capital': 0, 'total': 0}
            data_sum_row = data_sum[a_key]
            data_sum[a_key] = {'corriente': data_sum_row['corriente'] + row['corriente'],
                               'capital': data_sum_row['capital'] + row['capital'],
                               'total': data_sum_row['total'] + row['total'],
                               'anio': row['anio'], 'clasificacion': row['clasificacion']}
        data = data_sum.values()
        data = sorted(data, key=lambda k: (k['clasificacion'],
                                           k['anio']))
        # re-arrange data
        data_clase = {}
        for row in data:
            clase = row['clasificacion']
            data_clase[clase] = filter(
                lambda x: x['clasificacion'] == clase, data)

        years_list = sorted(list(iniciales) + list(finales))
        context['data_clase'] = data_clase
        context['years'] = years_list

        data_by_years = {}
        for year in years_list:
            data_by_years[year] = {
                'corriente': sum([row['corriente'] for row in data if row['anio'] == year]),
                'capital': sum([row['capital'] for row in data if row['anio'] == year]),
            }

        context['data_by_years'] = data_by_years

    context['data'] = data

    return context


def transferencias(request):
    context = {}

    data = getTransferencias(request.GET.get('municipio'))

    context['municipio'] = data.get('municipio')
    context['data'] = data.get('data')
    context['data_clase'] = data.get('data_clase')
    context['data_asignacion'] = data.get('data_asignacion')
    context['asignaciones'] = data.get('asignaciones')
    context['years'] = data.get('years')
    if data.get('data_by_years'):
        context['data_by_years'] = data.get('data_by_years')

    iniciales = AnioTransferencia.objects.values_list(
        'anio', flat=True).filter(periodo=PERIODO_INICIAL)
    finales = AnioTransferencia.objects.values_list(
        'anio', flat=True).filter(periodo=PERIODO_FINAL)
    inicial_filter = {'anio__in': iniciales, 'periodo': PERIODO_INICIAL}
    final_filter = {'anio__in': finales, 'periodo': PERIODO_FINAL}

    # obteniendo de manere ascendente los años con su pgr y pip
    anios_trans = list(AnioTransferencia.objects.order_by('anio').values(
        'anio', 'pgr', 'pip', 'recurso_tesoro_pip'))

    # Obteiendo totales de transferencias de capital y  corrientes por anio
    total_data_inicial = Transferencia.objects.order_by('anio').values('anio'). \
        filter(**inicial_filter).annotate(corriente=Sum('corriente'), capital=Sum('capital'),
                                          total=Sum('corriente') + Sum('capital'))
    total_data_final = Transferencia.objects.order_by('anio').values('anio'). \
        filter(**final_filter).annotate(corriente=Sum('corriente'), capital=Sum('capital'),
                                        total=Sum('corriente') + Sum('capital'))

    joined_total_data = list(total_data_inicial) + list(total_data_final)
    joined_total_data = sorted(joined_total_data, key=lambda d: d['anio'])

    # agregaremos nuevas key a joined_total_data
    for row in joined_total_data:
        anio_trans = filter(lambda i: i['anio'] == row['anio'], anios_trans)[0]
        pgr = xnumber(anio_trans['pgr'])
        pip = xnumber(anio_trans['pip'])
        recurso_tesoro_pip = xnumber(anio_trans['recurso_tesoro_pip'])

        row['pgr'] = pgr
        row['pip'] = pip
        row['recurso_tesoro_pip'] = recurso_tesoro_pip

        # calculando Porcentaje partida presupuestaria
        if row.get('pgr') > 0:
            row['partida'] = (xnumber(row.get('total')) / xnumber(row.get('pgr'))) * 100

        # % para destinar a inversión
        if row.get('total') > 0:
            row['porcentaje_inversion_ttotal'] = (
                xnumber(row.get('capital')) / xnumber(row.get('total'))) * 100

        if pip > 0:
            # calculando como % de los Recursos del Tesoro en el PIP en transferencias totales
            row['precurso_tesoro_ttotal'] = (xnumber(row.get('total')) / pip) * 100

            # como % del Programa de Inversiones Públicas
            row['pprograma_inversion_publica'] = (xnumber(row.get('capital')) / pip) * 100

        if recurso_tesoro_pip > 0:
            # como % de los Recursos del Tesoro en el PIP
            row['precurso_tesoro'] = (xnumber(row.get('capital')) / recurso_tesoro_pip) * 100

    context['evolucion'] = joined_total_data

    if request.GET.get('municipio2'):
        data = getTransferencias(request.GET.get('municipio2'))

        context['municipio2'] = data.get('municipio')
        context['data2'] = data.get('data')
        context['data_asignacion2'] = data.get('data_asignacion')
        context['years2'] = data.get('years')

    return render(request, 'transferencias.html', context)


def getPeriodosDetalle(datadata):
    context = {}
    prev_periodo = None
    data_tasa = {}
    tasas = {}
    municipios = []

    periodos = Periodo.objects. \
        all(). \
        order_by('desde')

    for periodo in periodos:
        periodo_key = "{}-{}".format(periodo.desde, periodo.hasta)
        data_tasa[periodo_key] = {}
        # temporalmente periodo +1
        anios = (periodo.hasta - periodo.desde) + 1
        ultimo_anio = {}
        ultimo_anio_previo = {}
        for row in datadata:
            municipio = row['municipio__nombre']
            if municipio not in municipios:
                municipios.append(municipio)
                tasas[municipio] = {'total': [],
                                    'corriente': [],
                                    'capital': [],
                                    'partido': [],
                                    'clasificacion': [],
                                    'municipio_id': row['municipio__id']
                                    }
            anio = row['anio']
            total = {
                'total': row['total'],
                'corriente': row['corriente'],
                'capital': row['capital']
            }
            if prev_periodo and anio == prev_periodo.hasta:
                ultimo_anio_previo[municipio] = total
            if anio == periodo.hasta:
                ultimo_anio[municipio] = total
        for municipio in municipios:
            if ultimo_anio.get(municipio) and ultimo_anio_previo.get(municipio):
                municipio_id = tasas[municipio]['municipio_id']
                partido = Municipio.objects. \
                    filter(periodomunic__municipio__id=municipio_id,
                           periodomunic__periodo__id=periodo.id). \
                    values('periodomunic__partido'). \
                    first()

                clasificacion = ClasificacionMunicAno.objects. \
                    filter(municipio_id=municipio_id,
                           anio=periodo.hasta). \
                    values('clasificacion__clasificacion'). \
                    first()['clasificacion__clasificacion']

                if ultimo_anio_previo[municipio]['total']:
                    tasa = growthRate(ultimo_anio[municipio]['total'],
                                      ultimo_anio_previo[municipio]['total'],
                                      anios)
                else:
                    tasa = 0
                if ultimo_anio_previo[municipio]['corriente']:
                    tasa_cr = growthRate(ultimo_anio[municipio]['corriente'],
                                         ultimo_anio_previo[municipio]['corriente'],
                                         anios)
                else:
                    tasa_cr = 0
                if ultimo_anio_previo[municipio]['capital']:
                    tasa_cp = growthRate(ultimo_anio[municipio]['capital'],
                                         ultimo_anio_previo[municipio]['capital'],
                                         anios)
                else:
                    tasa_cp = 0
                data_tasa[periodo_key][municipio] = tasa
                tasas[municipio]['total'].append(tasa)
                tasas[municipio]['corriente'].append(tasa_cr)
                tasas[municipio]['capital'].append(tasa_cp)
                if partido:
                    tasas[municipio]['partido'].append(partido['periodomunic__partido'])
                else:
                    tasas[municipio]['partido'].append('')
                tasas[municipio]['clasificacion'].append(clasificacion)
            else:
                tasas[municipio]['total'].append('')
                tasas[municipio]['corriente'].append('')
                tasas[municipio]['capital'].append('')
                tasas[municipio]['partido'].append('')
                tasas[municipio]['clasificacion'].append('')
        prev_periodo = periodo

    context['data_tasa'] = tasas
    context['municipios'] = municipios
    context['periodos'] = periodos

    return context


def getPeriodos(datadata, municipio=None):
    context = {}
    prev_periodo = None
    data_tasa = {}
    tasas = {}
    clasificaciones = []

    if municipio:
        partidos = Periodo.objects. \
            filter(periodomunic__municipio__slug=municipio). \
            values(periodo=Concat(
                'desde', V('-'), 'hasta', output_field=CharField()),
                nombre=F('periodomunic__partido')). \
            order_by('desde')

        context['partidos'] = partidos

    periodos = Periodo.objects. \
        all(). \
        order_by('desde')

    for periodo in periodos:
        periodo_key = "{}-{}".format(periodo.desde, periodo.hasta)
        data_tasa[periodo_key] = {}
        # temporalmente periodo +1
        anios = (periodo.hasta - periodo.desde) + 1
        ultimo_anio = {}
        ultimo_anio_previo = {}
        for row in datadata:
            clasificacion = row['clasificacion']
            if clasificacion not in clasificaciones:
                clasificaciones.append(clasificacion)
                tasas[clasificacion] = {'total': [],
                                        'corriente': [],
                                        'capital': []
                                        }
            anio = row['anio']
            total = {
                'total': row['total'],
                'corriente': row['corriente'],
                'capital': row['capital']
            }
            if prev_periodo and anio == prev_periodo.hasta:
                ultimo_anio_previo[clasificacion] = total
            if anio == periodo.hasta:
                ultimo_anio[clasificacion] = total
        for clasificacion in clasificaciones:
            if ultimo_anio.get(clasificacion) and ultimo_anio_previo.get(clasificacion):
                tasa = growthRate(ultimo_anio[clasificacion]['total'],
                                  ultimo_anio_previo[clasificacion]['total'],
                                  anios)
                tasa_cr = growthRate(ultimo_anio[clasificacion]['corriente'],
                                     ultimo_anio_previo[clasificacion]['corriente'],
                                     anios)
                tasa_cp = growthRate(ultimo_anio[clasificacion]['capital'],
                                     ultimo_anio_previo[clasificacion]['capital'],
                                     anios)
                data_tasa[periodo_key][clasificacion] = tasa
                tasas[clasificacion]['total'].append(tasa)
                tasas[clasificacion]['corriente'].append(tasa_cr)
                tasas[clasificacion]['capital'].append(tasa_cp)
            else:
                tasas[clasificacion]['total'].append('')
                tasas[clasificacion]['corriente'].append('')
                tasas[clasificacion]['capital'].append('')
        prev_periodo = periodo

    context['data_tasa'] = tasas
    context['clasificaciones'] = clasificaciones
    context['periodos'] = periodos

    return context


def tasa_transferencias(request):
    context = {}
    municipio = request.GET.get('municipio')
    municipio2 = request.GET.get('municipio2')

    data = getTransferencias(municipio)
    data_periodo = getPeriodos(data.get('data'), municipio)

    data_detalle = getTransferenciasDetalle()
    data_periodo_detalle = getPeriodosDetalle(data_detalle.get('data'))
    data_tasa_detalle = data_periodo_detalle.get('data_tasa')
    data_tasa_col = []
    for key in data_tasa_detalle:
        row = data_tasa_detalle[key]['total']
        cantidad_registros = len(data_tasa_detalle[key]['partido']) - 1
        ultimo_partido = data_tasa_detalle[key]['partido'][cantidad_registros]
        ultima_clasificacion = data_tasa_detalle[key]['clasificacion'][cantidad_registros]
        i = 0
        for col in row:
            if len(data_tasa_col) <= i:
                data_tasa_col.append([])
            if col:
                data_tasa_col[i].append({
                    'name': key,
                    'value': col,
                    'partido': ultimo_partido,
                    'clasificacion': ultima_clasificacion
                })
            i += 1

    data_tasa_col_sorted_asc = []
    data_tasa_col_sorted_des = []
    for col in data_tasa_col:
        col = sorted(col, key=lambda d: d['value'])
        data_tasa_col_sorted_asc.append(col)
        col = sorted(col, key=lambda d: d['value'], reverse=True)
        data_tasa_col_sorted_des.append(col)

    print(data_tasa_col_sorted_des)

    context['municipio'] = data.get('municipio')
    context['data_tasa'] = data_periodo.get('data_tasa')
    context['clasificaciones'] = data_periodo.get('clasificaciones')
    context['periodos'] = data_periodo.get('periodos')
    context['periodos_array'] = list(data_periodo.get('periodos'))
    context['partidos'] = data_periodo.get('partidos')
    context['data_tasa_detalle'] = data_periodo_detalle.get('data_tasa')
    context['data_tasa_col_des'] = data_tasa_col_sorted_des
    context['data_tasa_col_asc'] = data_tasa_col_sorted_asc

    if municipio2:
        data2 = getTransferencias(municipio2)
        data_periodo2 = getPeriodos(data2.get('data'), municipio2)
        context['municipio2'] = data2.get('municipio')
        context['data_tasa_municipio2'] = data_periodo2.get('data_tasa')
        context['clasificaciones2'] = data_periodo2.get('clasificaciones')
        context['periodos'] = data_periodo2.get('periodos')
        context['partidos_municpio2'] = data_periodo2.get('partidos')

    return render(request, 'tasa_transferencias.html', context)


def evolucion_transferencias(request):
    context = {}

    data = getTransferencias(request.GET.get('municipio'))

    iniciales = AnioTransferencia.objects.values_list(
        'anio', flat=True).filter(periodo=PERIODO_INICIAL)
    finales = AnioTransferencia.objects.values_list(
        'anio', flat=True).filter(periodo=PERIODO_FINAL)
    inicial_filter = {'anio__in': iniciales, 'periodo': PERIODO_INICIAL}
    final_filter = {'anio__in': finales, 'periodo': PERIODO_FINAL}

    # obteniendo de manere ascendente los años con su pgr y pip
    anios_trans = list(AnioTransferencia.objects.order_by('anio').values(
        'anio', 'pgr', 'pip', 'recurso_tesoro_pip'))

    # Obteiendo totales de transferencias de capital y  corrientes por anio
    total_data_inicial = Transferencia.objects.order_by('anio').values('anio'). \
        filter(**inicial_filter).annotate(corriente=Sum('corriente'), capital=Sum('capital'),
                                          total=Sum('corriente') + Sum('capital'))
    total_data_final = Transferencia.objects.order_by('anio').values('anio'). \
        filter(**final_filter).annotate(corriente=Sum('corriente'), capital=Sum('capital'),
                                        total=Sum('corriente') + Sum('capital'))

    joined_total_data = list(total_data_inicial) + list(total_data_final)
    joined_total_data = sorted(joined_total_data, key=lambda d: d['anio'])

    # agregaremos nuevas key a joined_total_data
    for row in joined_total_data:
        anio_trans = filter(lambda i: i['anio'] == row['anio'], anios_trans)[0]
        pgr = xnumber(anio_trans['pgr'])
        pip = xnumber(anio_trans['pip'])
        recurso_tesoro_pip = xnumber(anio_trans['recurso_tesoro_pip'])

        row['pgr'] = pgr
        row['pip'] = pip
        row['recurso_tesoro_pip'] = recurso_tesoro_pip

        # calculando Porcentaje partida presupuestaria
        if row.get('pgr') > 0:
            row['partida'] = (xnumber(row.get('total')) / xnumber(row.get('pgr'))) * 100

        # % para destinar a inversión
        if row.get('total') > 0:
            row['porcentaje_inversion_ttotal'] = (
                xnumber(row.get('capital')) / xnumber(row.get('total'))) * 100

        if pip > 0:
            # calculando como % de los Recursos del Tesoro en el PIP en transferencias totales
            row['precurso_tesoro_ttotal'] = (xnumber(row.get('total')) / pip) * 100

            # como % del Programa de Inversiones Públicas
            row['pprograma_inversion_publica'] = (xnumber(row.get('capital')) / pip) * 100

        if recurso_tesoro_pip > 0:
            # como % de los Recursos del Tesoro en el PIP
            row['precurso_tesoro'] = (xnumber(row.get('capital')) / recurso_tesoro_pip) * 100

    context['municipio'] = data.get('municipio')
    context['data'] = joined_total_data
    context['data_clase'] = data.get('data_clase')
    context['data_asignacion'] = data.get('data_asignacion')
    context['asignaciones'] = data.get('asignaciones')
    context['years'] = data.get('years')

    return render(request, 'evolucion_transferencias.html', context)
