# -*- coding: utf-8 -*-

from models import Proyecto
from django.utils.translation import ugettext_lazy as _
from model_report.report import reports, ReportAdmin
from model_report.utils import (usd_format, avg_column, sum_column, count_column)

class PlanInversionModelReport(ReportAdmin):
    title = u'Plan de inversión'
    model = Proyecto
    fields = [
        'inversion__year',
        'inversion__municipio__slug',
        'nombre',
        'catinversion__nombre',
        'asignado',
        'ejecutado',
        'self.porcentaje_ejecutado',
    ]
    override_field_labels = {
        'nombre': 'Proyecto',
        'inversion__municipio__slug': 'Municipio',
        'self.porcentaje_ejecutado': 'Porcentaje ejecutado',
        'catinversion__nombre': u'Categoría',
        #'date__day': lambda x, y: _('Day'),
    }
    list_filter = ('inversion__year','inversion__municipio__slug')
    list_order_by = ('nombre',)
    type = 'report'

reports.register('plan-de-inversion', PlanInversionModelReport)
