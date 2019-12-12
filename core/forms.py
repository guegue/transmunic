# -*- coding: utf-8 -*-
from django import forms
from lugar.models import Municipio
from core.models import PERIODO_CHOICES, CatInversion
import datetime


class UploadExcelForm(forms.Form):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(UploadExcelForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['municipio'].queryset = Municipio.objects.for_user(user)

    CHOICES = [('ingreso', 'Ingreso'), ('gasto', 'Gasto')]
    table = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES, required=True)
    municipio = forms.ModelChoiceField(queryset=Municipio.objects.all(),
                                       empty_label="(Municipio)",
                                       widget=forms.ChoiceField.widget(
                                           attrs={'class': "form-control required"})
                                       )
    year = forms.IntegerField(label=u"Año", widget=forms.IntegerField.widget(
        attrs={'class': "form-control required"}),
                              initial=lambda: datetime.date.today().year, required=True)
    periodo = forms.ChoiceField(choices=PERIODO_CHOICES, widget=forms.ChoiceField.widget(
        attrs={'class': "form-control required"}), required=True)
    start_row = forms.IntegerField(min_value=1, max_value=1000,
                                   widget=forms.IntegerField.widget(
                                       attrs={'class': "form-control required"})
                                   )
    end_row = forms.IntegerField(min_value=1, max_value=10000,
                                 widget=forms.IntegerField.widget(
                                     attrs={'class': "form-control required"})
                                 )
    excel_file = forms.FileField(widget=forms.FileField.widget(
        attrs={'class': 'form-control required'}
    )
    )


class DetallePresupuestoForm(forms.Form):
    MODELS = (
        ("Inversion", u"Inversión"),
        ("Ingreso", u"Ingreso"),
        ("Gasto", u"Gasto")
    )
    periodo = forms.ChoiceField(choices=PERIODO_CHOICES,
                                widget=forms.ChoiceField.widget(
                                    attrs={'class': "form-control required"},
                                ),
                                required=True
                                )
    year = forms.IntegerField(label=u"Año",
                              widget=forms.IntegerField.widget(
                                  attrs={'class': "form-control required"},
                              ),
                              initial=lambda: datetime.date.today().year,
                              required=True
                              )
    municipio = forms.ModelChoiceField(queryset=Municipio.objects.all(),
                                       widget=forms.ModelChoiceField.widget(
                                           attrs={'class': "form-control required"},
                                       ),
                                       required=True
                                       )
    tipo = forms.ChoiceField(choices=MODELS,
                             widget=forms.ChoiceField.widget(
                                 attrs={'class': "form-control required"},
                             ),
                             required=True
                             )
    catinversion = forms.ModelChoiceField(queryset=CatInversion.objects.all(),
                                          widget=forms.ModelChoiceField.widget(
                                              attrs={'class': "form-control required"},
                                          ),
                                          required=True
                                          )


class RenglonIngresoForm(forms.Form):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(RenglonIngresoForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['municipio'].queryset = Municipio.objects.for_user(user)

    municipio = forms.ModelChoiceField(queryset=Municipio.objects.all(),
                                       empty_label="(Municipio)",
                                       widget=forms.ChoiceField.widget(
                                           attrs={'class': "form-control required"})
                                       )
    year = forms.IntegerField(label=u"Año", widget=forms.IntegerField.widget(
        attrs={'class': "form-control required"}),
                              initial=lambda: datetime.date.today().year, required=True)
    periodo = forms.ChoiceField(choices=PERIODO_CHOICES, widget=forms.ChoiceField.widget(
        attrs={'class': "form-control required"}), required=True)
