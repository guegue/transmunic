from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.views.generic import FormView, DetailView

from openpyxl import load_workbook

from core.models import (Ingreso, IngresoDetalle, TipoIngreso, SubTipoIngreso, SubSubTipoIngreso,
                         IngresoRenglon)
from core.forms import UploadExcelForm
from core.tools import xnumber


def import_file(excel_file, municipio, year, periodo, start_row, end_row):
    book = load_workbook(filename=excel_file)
    sheet = book.active
    today = date.today()
    ingreso, created = Ingreso.objects.get_or_create(municipio=municipio, anio=year,
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
                    tipo, created = TipoIngreso.objects.get_or_create(codigo=codigo,
                                                                      defaults={'nombre': nombre})
                else:
                    subsubtipo, created = SubTipoIngreso.\
                        objects.get_or_create(codigo=codigo, tipoingreso_id=tipo_id,
                                              defaults={'nombre': nombre})
            else:
                subsubtipo, created = SubSubTipoIngreso.\
                    objects.get_or_create(codigo=codigo, subtipoingreso_id=subtipo_id,
                                          defaults={'nombre': nombre})
        else:
            # entrada en detalle (referencia a renglon)
            renglon, created = IngresoRenglon.\
                    objects.get_or_create(codigo=codigo,
                                          defaults={'subsubtipoingreso_id': subsubtipo_id,
                                                    'nombre': nombre})
            asignado = xnumber(row[1].value)
            ejecutado = xnumber(row[2].value)
            ingresodetalle, created = IngresoDetalle.\
                objects.update_or_create(codigo=codigo, ingreso=ingreso,
                                         defaults={'asignado': asignado, 'ejecutado': ejecutado,
                                                   'cuenta': nombre, 'tipoingreso_id': tipo_id,
                                                   'subtipoingreso_id': subtipo_id,
                                                   'subsubtipoingreso_id': subsubtipo_id})
    return ingreso


class UploadExcelView(LoginRequiredMixin, FormView):
    template_name = 'upload_excel.html'
    form_class = UploadExcelForm
    ingreso = 0

    def get_form_kwargs(self):
        kwargs = super(UploadExcelView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse('ingreso-detail', kwargs={'pk': self.ingreso.pk})

    def form_valid(self, form):
        data = form.cleaned_data
        if hasattr(self.request.user, 'profile') and\
                self.request.user.profile.municipio != data['municipio']:
            raise PermissionDenied("Limite de municipio excedido {} <> {}.".
                                   format(self.request.user.profile.municipio, data['municipio']))
        self.ingreso = import_file(self.request.FILES['excel_file'], municipio=data['municipio'],
                                   year=data['year'], periodo=data['periodo'],
                                   start_row=data['start_row'], end_row=data['end_row'])

        return super(UploadExcelView, self).form_valid(form)


class IngresoDetailView(LoginRequiredMixin, DetailView):
    model = Ingreso
