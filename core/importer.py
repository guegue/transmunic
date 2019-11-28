from datetime import date

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.views.generic import FormView, DetailView
from django.db.models import F
from openpyxl import load_workbook


from core.models import (Ingreso, IngresoDetalle, TipoIngreso, SubTipoIngreso, SubSubTipoIngreso,
                         IngresoRenglon, Gasto, GastoDetalle, TipoGasto, SubTipoGasto,
                         SubSubTipoGasto, GastoRenglon)
from core.forms import UploadExcelForm, RenglonIngresoForm
from core.tools import xnumber


def import_file(excel_file, municipio, year, periodo, start_row, end_row, table):
    tables = {'ingreso': {'main': Ingreso, 'detalle': IngresoDetalle, 'tipo': TipoIngreso,
                          'subtipo': SubTipoIngreso, 'subsubtipo': SubSubTipoIngreso,
                          'renglon': IngresoRenglon},
              'gasto': {'main': Gasto, 'detalle': GastoDetalle, 'tipo': TipoGasto,
                        'subtipo': SubTipoGasto, 'subsubtipo': SubSubTipoGasto,
                        'renglon': GastoRenglon}}
    t = tables[table]
    book = load_workbook(filename=excel_file)
    sheet = book.active
    today = date.today()
    main_object, created = t['main'].objects.get_or_create(municipio=municipio, anio=year,
                                                     periodo=periodo, defaults={'fecha': today})

    for row in sheet[start_row:end_row]:
        joined = unicode(row[0].value)
        if ' ' not in joined:
            continue
        (codigo, nombre) = row[0].value.split(' ', 1)
        tipo = codigo[0:2]
        tipo_id = "{}000000".format(tipo)
        subtipo = codigo[2:4]
        subtipo_id = "{}{}0000".format(tipo, subtipo)
        subsubtipo = codigo[4:6]
        subsubtipo_id = "{}{}{}00".format(tipo, subtipo, subsubtipo)
        cuenta = codigo[6:8]
        if cuenta == '00':
            # no agrega un entrada en detalle
            if subsubtipo == '00':
                if subtipo == '00':
                    if tipo == '00':
                        raise('Tipo no puede ser 00')
                    tipo, created = t['tipo'].objects.get_or_create(codigo=codigo,
                                                                      defaults={'nombre': nombre})
                else:
                    lookup_dict = {'codigo': codigo, 'tipo{}_id'.format(table): tipo_id}
                    print(lookup_dict)
                    print("OK")
                    print(t['subtipo'])
                    subsubtipo, created = t['subtipo'].objects.\
                        get_or_create(defaults={'nombre': nombre}, **lookup_dict)
            else:
                lookup_dict = {'codigo': codigo, 'subtipo{}_id'.format(table): subtipo_id}
                subsubtipo, created = t['subsubtipo'].\
                    objects.get_or_create(defaults={'nombre': nombre}, **lookup_dict)
        else:
            # entrada en detalle (referencia a renglon)
            lookup_dict = {'codigo': codigo, 'subsubtipo{}_id'.format(table): subsubtipo_id}
            renglon, created = t['renglon'].\
                objects.get_or_create(defaults={'nombre': nombre}, **lookup_dict)
            asignado = xnumber(row[1].value)
            ejecutado = xnumber(row[2].value)

            lookup_dict = {'codigo_id': codigo, table: main_object}
            detalle, created = t['detalle'].\
                objects.update_or_create(defaults={'asignado': asignado, 'ejecutado': ejecutado,
                                                   'cuenta': nombre,
                                                   'tipo{}_id'.format(table): tipo_id,
                                                   'subtipo{}_id'.format(table): subtipo_id,
                                                   'subsubtipo{}_id'.format(table): subsubtipo_id},
                                         **lookup_dict)

    return main_object


class UploadExcelView(LoginRequiredMixin, FormView):
    template_name = 'upload_excel.html'
    form_class = UploadExcelForm
    record = None

    def get_form_kwargs(self):
        kwargs = super(UploadExcelView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        table = self.record._meta.model_name
        return reverse('importar-resultado', kwargs={'table': table, 'pk': self.record.pk})

    def form_valid(self, form):
        data = form.cleaned_data
        if hasattr(self.request.user, 'profile') and \
                self.request.user.profile.municipio != data['municipio']:
            raise PermissionDenied("Limite de municipio excedido {} <> {}.".
                                   format(self.request.user.profile.municipio, data['municipio']))
        self.record = import_file(self.request.FILES['excel_file'], municipio=data['municipio'],
                                  year=data['year'], periodo=data['periodo'],
                                  start_row=data['start_row'], end_row=data['end_row'],
                                  table=data['table'])

        return super(UploadExcelView, self).form_valid(form)


class IngresoDetailView(LoginRequiredMixin, DetailView):
    model = Ingreso


class ReglonIngresosView(LoginRequiredMixin, FormView):
    template_name = 'reglon_ingreso.html'
    form_class = RenglonIngresoForm
    form = RenglonIngresoForm

    def form_valid(self, form):
        data = form.cleaned_data
        return super(ReglonIngresosView, self).form_valid(form)

    def get_success_url(self):
        return reverse('regloningreso')

    def get_context_data(self, **kwargs):
        tipos_ingresos = IngresoRenglon.objects. \
            order_by('subsubtipoingreso__subtipoingreso__tipoingreso__codigo'). \
            values(tipo_ing_codigo=F('subsubtipoingreso__subtipoingreso__tipoingreso__codigo'),
                   tipo_ing_nombre=F('subsubtipoingreso__subtipoingreso__tipoingreso__nombre')). \
            distinct()

        for row in tipos_ingresos:
            ingreso_reglon = IngresoRenglon.objects. \
                filter(
                    subsubtipoingreso__subtipoingreso__tipoingreso__codigo=row['tipo_ing_codigo']). \
                values('codigo', 'nombre').all()
            row['ingreso_reglon'] = ingreso_reglon

        context = super(ReglonIngresosView, self).get_context_data(**kwargs)
        context['tipos_ingresos'] = tipos_ingresos
        return context


class ResultadoDetailView(LoginRequiredMixin, DetailView):
    template_name = 'import_results.html'

    def get_object(self):
        self.model = apps.get_model('core', self.kwargs['table'])
        return super(ResultadoDetailView, self).get_object()
