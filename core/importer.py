from datetime import date

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.views.generic import FormView, DetailView
from django.db.models import F
from openpyxl import load_workbook

from core.models import (Ingreso, IngresoDetalle, TipoIngreso, SubTipoIngreso, SubSubTipoIngreso,
                         Sub3TipoIngreso, IngresoRenglon, Gasto, GastoDetalle, TipoGasto,
                         SubTipoGasto, SubSubTipoGasto, GastoRenglon)
from lugar.models import (Municipio)
from core.forms import UploadExcelForm, RenglonIngresoForm
from core.tools import xnumber


def import_file(excel_file, municipio, year, periodo, start_row, end_row, table):
    tables = {'ingreso': {'main': Ingreso, 'detalle': IngresoDetalle, 'tipo': TipoIngreso,
                          'subtipo': SubTipoIngreso, 'subsubtipo': SubSubTipoIngreso,
                          'sub3tipo': Sub3TipoIngreso,
                          'renglon': IngresoRenglon},
              'gasto': {'main': Gasto, 'detalle': GastoDetalle, 'tipo': TipoGasto,
                        'subtipo': SubTipoGasto, 'subsubtipo': SubSubTipoGasto,
                        'renglon': GastoRenglon}}
    t = tables[table]
    book = load_workbook(filename=excel_file)
    sheet = book.active
    today = date.today()
    main_object, created = t['main'].objects.\
        get_or_create(municipio=municipio,
                      anio=year,
                      periodo=periodo,
                      defaults={'fecha': today})

    # define structure
    sub3 = False
    tipo_start = 0
    year = int(year)
    if table == 'gasto':
        if year >= 2018:
            code_len = 5
            tipo_end = 1
            subtipo_start = 1
            subtipo_end = 2
            subsubtipo_start = 2
            subsubtipo_end = 3
            cuenta_start = 3
            cuenta_end = 5
        if year < 2018:
            code_len = 7
            tipo_end = 1
            subtipo_start = 1
            subtipo_end = 2
            subsubtipo_start = 2
            subsubtipo_end = 4
            cuenta_start = 4
            cuenta_end = 7
    if table == 'ingreso':
        if year >= 2018:
            sub3 = True
            code_len = 6
            tipo_end = 2
            subtipo_start = 2
            subtipo_end = 3
            subsubtipo_start = 3
            subsubtipo_end = 4
            sub3tipo_start = 4
            sub3tipo_end = 5
            cuenta_start = 5
            cuenta_end = 6
        if year < 2018:
            code_len = 8
            tipo_end = 2
            subtipo_start = 2
            subtipo_end = 4
            subsubtipo_start = 4
            subsubtipo_end = 6
            cuenta_start = 6
            cuenta_end = 8

    for row in sheet[start_row:end_row]:
        joined = unicode(row[0].value).replace(u'\xa0', u' ').strip()
        if ' ' not in joined:
            continue
        (codigo, nombre) = joined.split(' ', 1)
        codigo = codigo.ljust(code_len, '0')
        tipo = codigo[tipo_start:tipo_end]
        tipo_id = tipo.ljust(code_len, '0')
        subtipo = codigo[subtipo_start:subtipo_end]
        print('subtipo:' + subtipo)
        subtipo_id = "{}{}".format(tipo, subtipo)
        subtipo_id = subtipo_id.ljust(code_len, '0')
        print('subtipo_id:' + subtipo_id)
        subsubtipo = codigo[subsubtipo_start:subsubtipo_end]
        subsubtipo_id = "{}{}{}".format(tipo, subtipo, subsubtipo)
        subsubtipo_id = subsubtipo_id.ljust(code_len, '0')
        if sub3:
            sub3tipo = codigo[sub3tipo_start:sub3tipo_end]
            sub3tipo_id = "{}{}{}{}".format(tipo, subtipo, subsubtipo, sub3tipo)
            sub3tipo_id = sub3tipo_id.ljust(code_len, '0')
        cuenta = codigo[cuenta_start:cuenta_end]
        print(codigo)
        if int(cuenta) == 0:
            # no agrega un entrada en detallea
            if (sub3 and int(sub3tipo) == 0) or (not sub3):
                if int(subsubtipo) == 0:
                    if int(subtipo) == 0:
                        if int(tipo) == 0:
                            raise ('Tipo no puede ser 0')
                        tipo, created = t['tipo'].objects.get_or_create(codigo=codigo,
                                                                        defaults={'nombre': nombre})
                    else:
                        print('create subtipo')
                        lookup_dict = {'codigo': codigo, 'tipo{}_id'.format(table): tipo_id}
                        subtipo, created = t['subtipo'].objects.\
                            get_or_create(defaults={'nombre': nombre}, **lookup_dict)
                else:
                    print('create subsubtipo, con padre {}'.format(subtipo_id))
                    lookup_dict = {'codigo': codigo, 'subtipo{}_id'.format(table): subtipo_id}
                    subsubtipo, created = t['subsubtipo']. \
                        objects.get_or_create(defaults={'nombre': nombre}, **lookup_dict)
            elif sub3:
                print('create sub3tipo')
                lookup_dict = {'codigo': codigo, 'subsubtipo{}_id'.format(table): subsubtipo_id}
                sub3tipo, created = t['sub3tipo']. \
                    objects.get_or_create(defaults={'nombre': nombre}, **lookup_dict)
        else:
            # entrada en detalle (referencia a renglon)
            if sub3:
                lookup_dict = {'codigo': codigo, 'sub3tipo{}_id'.format(table): sub3tipo_id}
            else:
                lookup_dict = {'codigo': codigo, 'subsubtipo{}_id'.format(table): subsubtipo_id}
            renglon, created = t['renglon']. \
                objects.get_or_create(defaults={'nombre': nombre}, **lookup_dict)
            asignado = xnumber(row[1].value)
            ejecutado = xnumber(row[2].value)

            lookup_dict = {'codigo_id': codigo, table: main_object}
            defaults_dict = {'asignado': asignado, 'ejecutado': ejecutado,
                                                   'cuenta': nombre,
                                                   'tipo{}_id'.format(table): tipo_id,
                                                   'subtipo{}_id'.format(table): subtipo_id,
                                                   'subsubtipo{}_id'.format(table): subsubtipo_id}
            if sub3:
                defaults_dict['sub3tipo{}_id'.format(table)] = sub3tipo_id

            detalle, created = t['detalle'].objects.update_or_create(defaults=defaults_dict,
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
    template_name = 'renglon_ingreso.html'
    form_class = RenglonIngresoForm
    form = RenglonIngresoForm

    def get_form_kwargs(self):
        kwargs = super(ReglonIngresosView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        data = form.cleaned_data
        if hasattr(self.request.user, 'profile') and \
                self.request.user.profile.municipio != data['municipio']:
            raise PermissionDenied("Limite de municipio excedido {} <> {}.".
                                   format(self.request.user.profile.municipio, data['municipio']))
        # get the data from the form
        renglon_codigo = self.request.POST.getlist('renglon[codigo]')
        municipio = self.request.POST.get('municipio')
        anio = self.request.POST.get('year')
        periodo = self.request.POST.get('periodo')

        # obteniendo detalles del municipio seleccionado
        municipio = Municipio.objects.filter(id=municipio).first()

        # insertando en core_ingreso
        ingreso = Ingreso()
        ingreso.fecha = date.today()
        ingreso.departamento_id = municipio.depto_id
        ingreso.municipio_id = municipio.id
        ingreso.anio = anio
        ingreso.periodo = periodo
        ingreso.save()

        # insertando en core_ingresodetalle
        for codigo in renglon_codigo:
            # obteniendo el asignado y ejecutado de un renglon
            renglon_asignado = self.request.POST.get('renglon_{}_asignado'.format(codigo))
            renglon_ejecutado = self.request.POST.get('renglon_{}_ejecutado'.format(codigo))
            if xnumber(renglon_asignado) > 0 and xnumber(renglon_ejecutado) > 0:
                subsubtipo = SubSubTipoIngreso.objects. \
                    filter(ingresorenglon__codigo=codigo). \
                    values(id_subsubtipo=F('codigo'),
                           id_subtipo=F('subtipoingreso__codigo'),
                           id_tipo=F('subtipoingreso__tipoingreso_id')). \
                    first()

                # guardando el detalle de cada renglon
                ingreso_detalle = IngresoDetalle()
                ingreso_detalle.codigo_id = codigo
                ingreso_detalle.asignado = xnumber(renglon_asignado)
                ingreso_detalle.ejecutado = xnumber(renglon_ejecutado)
                ingreso_detalle.ingreso_id = ingreso.id
                ingreso_detalle.subsubtipoingreso_id = subsubtipo.get('id_subsubtipo')
                ingreso_detalle.subtipoingreso_id = subsubtipo.get('id_subtipo')
                ingreso_detalle.tipoingreso_id = subsubtipo.get('id_tipo')
                ingreso_detalle.cuenta = 'SA'
                ingreso_detalle.save()

        return super(ReglonIngresosView, self).form_valid(form)

    def get_success_url(self):
        return reverse('rengloningreso')

    def get_context_data(self, **kwargs):
        tipos_ingresos = IngresoRenglon.objects. \
            order_by('subsubtipoingreso__subtipoingreso__tipoingreso__codigo'). \
            values(tipo_ing_codigo=F('subsubtipoingreso__subtipoingreso__tipoingreso__codigo'),
                   tipo_ing_nombre=F('subsubtipoingreso__subtipoingreso__tipoingreso__nombre')). \
            distinct()

        for row in tipos_ingresos:
            ingreso_renglon = IngresoRenglon.objects. \
                filter(
                    subsubtipoingreso__subtipoingreso__tipoingreso__codigo=row['tipo_ing_codigo']). \
                values('codigo', 'nombre').all()
            row['ingreso_renglon'] = ingreso_renglon

        context = super(ReglonIngresosView, self).get_context_data(**kwargs)
        context['tipos_ingresos'] = tipos_ingresos
        return context


class ResultadoDetailView(LoginRequiredMixin, DetailView):
    template_name = 'import_results.html'

    def get_object(self):
        self.model = apps.get_model('core', self.kwargs['table'])
        return super(ResultadoDetailView, self).get_object()
