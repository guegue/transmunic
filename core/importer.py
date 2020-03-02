# -*- coding: utf-8 -*-

from datetime import date

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.urls import reverse
from django.views.generic import FormView, DetailView
from django.db.models import F
from django.contrib import messages
from openpyxl import load_workbook

from core.models import (Ingreso, IngresoDetalle, TipoIngreso, SubTipoIngreso, SubSubTipoIngreso,
                         Sub3TipoIngreso, IngresoRenglon, Gasto, GastoDetalle, TipoGasto,
                         SubTipoGasto, SubSubTipoGasto, GastoRenglon,
                         Inversion, Proyecto, CatInversion, Transferencia)
from lugar.models import (Municipio)
from core.forms import UploadExcelForm, RenglonForm
from core.tools import xnumber


def not_or_zero(value, active_zero):
    if value == '':
        return True
    if not active_zero and int(value) == 0:
        return True
    return False

def import_file(excel_file, municipio, year, periodo, start_row, end_row, table):
    tables = {'ingreso': {'main': Ingreso, 'detalle': IngresoDetalle, 'tipo': TipoIngreso,
                          'subtipo': SubTipoIngreso, 'subsubtipo': SubSubTipoIngreso,
                          'sub3tipo': Sub3TipoIngreso,
                          'renglon': IngresoRenglon},
              'gasto': {'main': Gasto, 'detalle': GastoDetalle, 'tipo': TipoGasto,
                        'subtipo': SubTipoGasto, 'subsubtipo': SubSubTipoGasto,
                        'renglon': GastoRenglon},
              'inversion': {'main': Inversion, 'detalle': Proyecto, 'tipo': CatInversion},
              'transferencia': {'main': Transferencia, },
              }
    t = tables[table]
    book = load_workbook(filename=excel_file)
    sheet = book.active
    today = date.today()
    year = int(year)

    # proceso para 'transferencia' es diferente, no hay main_object (o detalle)
    if table == 'transferencia':
        for row in sheet[start_row:end_row]:
            municipio = Municipio.objects.filter(\
                    nombre__unaccent__iexact=unicode(row[0].value)).first()
            if not municipio:
                municipio = Municipio.objects.filter(nombre=row[0].value).first()
            if not municipio:
                raise ObjectDoesNotExist(u'Municipio "%s" no existe' % (row[0].value,))

            aobject, created = t['main'].objects.\
                update_or_create(municipio=municipio,
                    anio=year,
                    periodo=periodo,
                    defaults={'fecha': today, 'corriente': xnumber(row[1].value),
                              'capital': xnumber(row[2].value)})
        return aobject
    # enf of 'transferencia' import

    main_object, created = t['main'].objects.\
        get_or_create(municipio=municipio,
                      anio=year,
                      periodo=periodo,
                      defaults={'fecha': today})

    # proceso para 'inversion' es diferente, menos tablas relacionadas
    if table == 'inversion':
        for row in sheet[start_row:end_row]:
            if year >= 2018:
                catinversion_str = unicode(row[2].value)
                try:
                    catinversion_str = unicode(row[2].value)
                    catinversion = t['tipo'].objects.get(nombre=catinversion_str)
                except ObjectDoesNotExist:
                    raise ObjectDoesNotExist(
                        u'Categoría de Inversión "%s" no existe' % (catinversion_str,))

                nombre = unicode(row[1].value)
                asignado = xnumber(row[3].value)
                ejecutado = xnumber(row[4].value)
                defaults_dict = {'asignado': asignado, 'ejecutado': ejecutado,
                                 'catinversion': catinversion}
                proyecto, created = t['detalle'].objects.update_or_create(nombre=nombre,
                                                                          inversion=main_object,
                                                                          defaults=defaults_dict)
            else:
                catinversion_id = xnumber(row[2].value)
                try:
                    if catinversion_id:
                        catinversion = t['tipo'].objects.get(id=catinversion_id)
                    else:
                        catinversion_id = unicode(row[2].value)
                        catinversion = t['tipo'].objects.get(nombre=catinversion_id)
                except ObjectDoesNotExist:
                    raise ObjectDoesNotExist(
                        u'Categoría de Inversión %s no existe' % (catinversion_id,))

                areageografica = str(row[3].value)[0]
                nombre = unicode(row[1].value)
                asignado = xnumber(row[4].value)
                ejecutado = xnumber(row[5].value)
                defaults_dict = {'asignado': asignado, 'ejecutado': ejecutado,
                                 'catinversion': catinversion, 'areageografica': areageografica, }
                proyecto, created = t['detalle'].objects.update_or_create(nombre=nombre,
                                                                          inversion=main_object,
                                                                          defaults=defaults_dict)
        return main_object

    # define structure
    sub3 = False
    active_zero = False
    tipo_start = 0
    if table == 'gasto':
        if year >= 2018:
            active_zero = True
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
            subsubtipo_end = 3
            cuenta_start = 3
            cuenta_end = 7
    if table == 'ingreso':
        if year >= 2018:
            active_zero = True
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
        tipo = codigo[tipo_start:tipo_end]
        tipo_id = tipo
        subtipo = codigo[subtipo_start:subtipo_end]
        subtipo_id = "{}{}".format(tipo, subtipo)
        subsubtipo = codigo[subsubtipo_start:subsubtipo_end]
        subsubtipo_id = "{}{}{}".format(tipo, subtipo, subsubtipo)
        if sub3:
            sub3tipo = codigo[sub3tipo_start:sub3tipo_end]
            sub3tipo_id = "{}{}{}{}".format(tipo, subtipo, subsubtipo, sub3tipo)
            if not active_zero:
                sub3tipo_id = sub3tipo_id.ljust(code_len, '0')
        if not active_zero:
            codigo = codigo.ljust(code_len, '0')
            tipo_id = tipo.ljust(code_len, '0')
            subtipo_id = subtipo_id.ljust(code_len, '0')
            subsubtipo_id = subsubtipo_id.ljust(code_len, '0')
        cuenta = codigo[cuenta_start:cuenta_end]
        if not_or_zero(cuenta, active_zero):
            # no agrega un entrada en detallea
            if not sub3 or not_or_zero(sub3tipo, active_zero):
                if not_or_zero(subsubtipo, active_zero):
                    if not_or_zero(subtipo, active_zero):
                        if not_or_zero(tipo, active_zero):
                            raise ('Debe indicarse el tipo.')
                        tipo, created = t['tipo'].objects.get_or_create(codigo=codigo,
                                                                        defaults={'nombre': nombre})
                    else:
                        #print('create subtipo')
                        lookup_dict = {'codigo': codigo, 'tipo{}_id'.format(table): tipo_id}
                        subtipo, created = t['subtipo'].objects.\
                            get_or_create(defaults={'nombre': nombre}, **lookup_dict)
                else:
                    #print('create subsubtipo, con padre {}'.format(subtipo_id))
                    lookup_dict = {'codigo': codigo, 'subtipo{}_id'.format(table): subtipo_id}
                    subsubtipo, created = t['subsubtipo']. \
                        objects.get_or_create(defaults={'nombre': nombre}, **lookup_dict)
            elif sub3:
                #print('create sub3tipo')
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
        if data.get('municipio') and hasattr(self.request.user, 'profile') and \
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
    form_class = RenglonForm
    form = RenglonForm

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

        # validando si existe un ingreso en el sistema que este relacionado
        # a el municipio, en periodo del año indicados desdel formulario
        ingreso = Ingreso.objects.filter(municipio_id=municipio.id,
                               anio=anio,
                               periodo=periodo).first()

        if not ingreso:
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
                renglon_asignado = self.request.POST.get('renglon_asignado[{}]'.format(codigo))
                renglon_ejecutado = self.request.POST.get('renglon_ejecutado[{}]'.format(codigo))
                if xnumber(renglon_asignado) > 0 and xnumber(renglon_ejecutado) >= 0:
                    subsubtipo = Sub3TipoIngreso.objects. \
                        filter(ingresorenglon__codigo=codigo). \
                        values(id=F('codigo'),
                               id_subsubtipo=F('subsubtipoingreso_id'),
                               id_subtipo=F('subsubtipoingreso__subtipoingreso_id'),
                               id_tipo=F('subsubtipoingreso__subtipoingreso__tipoingreso_id')). \
                        first()

                    # guardando el detalle de cada renglon
                    ingreso_detalle = IngresoDetalle()
                    ingreso_detalle.codigo_id = codigo
                    ingreso_detalle.asignado = xnumber(renglon_asignado)
                    ingreso_detalle.ejecutado = xnumber(renglon_ejecutado)
                    ingreso_detalle.ingreso_id = ingreso.id
                    ingreso_detalle.sub3tipoingreso_id = subsubtipo.get('id')
                    ingreso_detalle.subsubtipoingreso_id = subsubtipo.get('id_subsubtipo')
                    ingreso_detalle.subtipoingreso_id = subsubtipo.get('id_subtipo')
                    ingreso_detalle.tipoingreso_id = subsubtipo.get('id_tipo')
                    ingreso_detalle.cuenta = 'SA'
                    ingreso_detalle.save()

            return super(ReglonIngresosView, self).form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, 'El municipio ya cuenta con un ingreso para el'
                                                           ' año seleccionado en el periodo indicado')
        return super(ReglonIngresosView, self).form_invalid(form)

    def get_success_url(self):
        messages.add_message(self.request, messages.INFO, 'Guardado Exitosamente')
        return reverse('rengloningreso')

    def get_context_data(self, **kwargs):
        label = 'sub3tipoingreso__subsubtipoingreso__subtipoingreso__tipoingreso__{}'
        tipoingreso_codigo_not_null = label.format('codigo__isnull')
        tipoingreso_codigo = label.format('codigo')
        tipoingreso_nombre = label.format('nombre')
        tipoingreso_nuevo_catalogo = label.format('nuevo_catalogo')
        filter_dict = {
            tipoingreso_codigo_not_null: False,
            tipoingreso_nuevo_catalogo: True
        }

        ''  # Consulta ORM para obtener los tipos de ingresos y sus renglones
        tipos_ingresos = IngresoRenglon.objects. \
            filter(**filter_dict). \
            order_by(tipoingreso_codigo). \
            values(tipoingreso_codigo=F(tipoingreso_codigo),
                   tipoingreso_nombre=F(tipoingreso_nombre),
                   rengloningreso_codigo=F('codigo'),
                   rengloningreso_nombre=F('nombre'))

        context = super(ReglonIngresosView, self).get_context_data(**kwargs)
        context['tipos_ingresos'] = tipos_ingresos
        return context


class RenglonGastosView(LoginRequiredMixin, FormView):
    template_name = 'renglon_gasto.html'
    form_class = RenglonForm
    form = RenglonForm

    def get_form_kwargs(self):
        kwargs = super(RenglonGastosView, self).get_form_kwargs()
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

        # validando si existe un gasto en el sistema que este relacionado
        # a el municipio, en periodo del año indicados desdel formulario
        gasto = Gasto.objects.filter(municipio_id=municipio.id,
                                     anio=anio,
                                     periodo=periodo).first()

        if not gasto:
            # insertando en core_gasto
            gasto = Gasto()
            gasto.fecha = date.today()
            gasto.departamento_id = municipio.depto_id
            gasto.municipio_id = municipio.id
            gasto.anio = anio
            gasto.periodo = periodo
            gasto.save()

            # insertando en core_ingresodetalle
            for codigo in renglon_codigo:
                # obteniendo el asignado y ejecutado de un renglon
                asignado = self.request.POST.get('renglon_asignado[{}]'.format(codigo))
                ejecutado = self.request.POST.get('renglon_ejecutado[{}]'.format(codigo))
                asignado = xnumber(asignado)
                ejecutado = xnumber(ejecutado)

                if asignado > 0 and ejecutado >= 0:
                    subsubtipo = SubSubTipoGasto.objects. \
                        filter(gastorenglon__codigo='11100'). \
                        values(id=F('codigo'),
                               id_subtipo=F('subtipogasto_id'),
                               id_tipo=F('subtipogasto__tipogasto_id')). \
                        first()

                    # guardando el detalle de cada renglon
                    gasto_detalle = GastoDetalle()
                    gasto_detalle.codigo_id = codigo
                    gasto_detalle.asignado = asignado
                    gasto_detalle.ejecutado = ejecutado
                    gasto_detalle.gasto_id = gasto.id
                    gasto_detalle.subsubtipogasto_id = subsubtipo.get('id')
                    gasto_detalle.subtipogasto_id = subsubtipo.get('id_subtipo')
                    gasto_detalle.tipogasto_id = subsubtipo.get('id_tipo')
                    gasto_detalle.cuenta = 'SA'
                    gasto_detalle.save()

            return super(RenglonGastosView, self).form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, 'El municipio ya cuenta con un gasto para el'
                                                           ' año seleccionado en el periodo indicado')
        return super(RenglonGastosView, self).form_invalid(form)

    def get_success_url(self):
        messages.add_message(self.request, messages.INFO, 'Guardado Exitosamente')
        return reverse('renglon-gasto')

    def get_context_data(self, **kwargs):
        label = 'subsubtipogasto__subtipogasto__tipogasto__{}'
        tipogasto_codigo_not_null = label.format('codigo__isnull')
        tipogasto_codigo = label.format('codigo')
        tipogasto_nombre = label.format('nombre')
        tipogasto_nuevo_catalogo = label.format('nuevo_catalogo')
        filter_dict = {
            tipogasto_codigo_not_null: False,
            tipogasto_nuevo_catalogo: True
        }

        ''  # Consulta ORM para obtener los tipos de gastos y sus renglones
        tipo_gastos = GastoRenglon.objects. \
            filter(**filter_dict). \
            order_by(tipogasto_codigo). \
            values(tipogasto_codigo=F(tipogasto_codigo),
                   tipogasto_nombre=F(tipogasto_nombre),
                   renglongasto_codigo=F('codigo'),
                   renglongasto_nombre=F('nombre'))

        context = super(RenglonGastosView, self).get_context_data(**kwargs)
        context['tipos_gastos'] = tipo_gastos
        return context


class ResultadoDetailView(LoginRequiredMixin, DetailView):
    template_name = 'import_results.html'

    def get_object(self):
        self.model = apps.get_model('core', self.kwargs['table'])
        return super(ResultadoDetailView, self).get_object()
