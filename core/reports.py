# -*- coding: utf-8 -*-

from models import Proyecto
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import Select, TextInput
from model_report.report import reports, ReportAdmin
from model_report.utils import (usd_format, avg_column, sum_column, count_column)

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
        'self.porcentaje_ejecutado',
    ]
    #list_filter_widget = {
     #   'inversion__anio': TextInput(),
    #}
    override_field_labels = {
        'inversion__anio': u'Año',
        'nombre': 'Proyecto',
        'inversion__municipio__nombre': 'Municipio',
        'self.porcentaje_ejecutado': 'Porcentaje ejecutado',
        #'catinversion__nombre': u'Categoría',
        #'date__day': lambda x, y: _('Day'),
    }
    list_filter = ('inversion__anio','inversion__municipio',)
    list_order_by = ('nombre',)
    type = 'report'

reports.register('plan-de-inversion', PlanInversionModelReport)
