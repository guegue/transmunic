# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import Select, TextInput
from django.utils.formats import number_format
from django.conf import settings

from model_report.report import reports, ReportAdmin
from model_report.utils import (usd_format, avg_column, sum_column, count_column)

from models import Proyecto, CatInversion


def intcomma(value, instance):
    if not value:
        return 0
    return number_format(value, force_grouping=True)


def link_to_media(rvalue, instance):
    if instance.is_value:
        return '<a href="%s%s">%s</a>' % (settings.MEDIA_URL, rvalue, rvalue)
    return rvalue.value[0]

class PlanInversionModelReport(ReportAdmin):


    title = u'Plan de inversión'
    model = Proyecto
    fields = [
        'inversion__anio',
        'inversion__municipio__nombre',
        'nombre',
        'catinversion__nombre',
        'asignado',
        'ejecutado',
        #'ficha',
        'self.porcentaje_ejecutado',
    ]
    years = [(year, year) for year in range(2010, 2017)]
    periodos = [(None, '--'), ('I', 'Inicial'), ('A', 'Actualizado'), ('F', 'Final')]
    list_filter_widget = {
        'inversion__anio': Select(choices=years),
        'inversion__periodo': Select(choices=periodos),
    }
    override_field_labels = {
        'inversion__anio': u'Año',
        'nombre': 'Proyecto',
        'inversion__municipio__nombre': 'Municipio',
        'self.porcentaje_ejecutado': 'Porcentaje ejecutado',
        'catinversion__nombre': u'Categoría',
        #'ficha': 'Ficha del proyecto',
        #'date__day': lambda x, y: _('Day'),
    }
    override_field_formats = {
        'asignado': intcomma,
        'ejecutado': intcomma,
        #'ficha': link_to_media,
    }
    list_filter = ('inversion__anio', 'inversion__periodo',
            'inversion__municipio','catinversion', 'nombre')
    #list_filter_op = {'nombre': 'startswith'}
    list_filter_op = {'nombre': 'icontains'}
    list_order_by = ('nombre',)
    type = 'report'


    def __init__(self, parent_report=None, request=None):
        self.fields = [
            'inversion__anio',
            'inversion__municipio__nombre',
            'nombre',
            'catinversion__nombre',
            'asignado',
            'ejecutado',
            'self.porcentaje_ejecutado',
            #'ficha',
        ]
        if request.GET.get('inversion__periodo') == 'F':
            self.fields.remove('asignado')
        if request.GET.get('inversion__periodo') == 'I':
            self.fields.remove('ejecutado')
        super(PlanInversionModelReport, self).__init__(parent_report, request)

# class DetallePresupuestoReport(object):
#     MODELS = (
#               ("InversionFuente",u"Inversión")
#               ("Ingreso",u"Ingreso"),
#               ("Gasto",u"Gasto"),              
#               )
#     MODEL_FIELDS = {
#               "InversionFuente":["fecha","anio",
#                                  "periodo","departamento","municipio"
#                                  ],
#                 "Ingreso":["fecha","anio",
#                                  "periodo","departamento","municipio",
#                                  "descripcion"
#                                  ],                    
#                 "Gasto":["fecha","anio",
#                                  "periodo","departamento","municipio",
#                                  "descripcion"
#                                  ],           
#               "InversionFuenteDetalle":[
#                                  "inversionfuente",
#                                  "tipofuente",
#                                  "fuente",
#                                  "asignado",
#                                  "ejecutado"
#                                  ],
#               "GastoDetalle":[
#                                  "gasto",
#                                  "codigo",
#                                  "tipogasto",
#                                  "subtipogasto",
#                                  "subsubtipogasto",
#                                  "cuenta",
#                                  "asignado",
#                                  "ejecutado"
#                                  ],
#               "IngresoDetalle":[
#                                  "ingreso",
#                                  "codigo",
#                                  "tipoingreso",
#                                  "subtipoingreso",
#                                  "subsubtipoingreso",
#                                  "cuenta",
#                                  "asignado",
#                                  "ejecutado"
#                                  ],                                                             
#               }
#     title = u'Detalle del Presupuesto'

reports.register('plan-de-inversion', PlanInversionModelReport)
