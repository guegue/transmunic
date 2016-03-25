# -*- coding: utf-8 -*-
from django import forms
from lugar.models import Municipio
from core.models import PERIODO_CHOICES
import datetime
class DetallePresupuestoForm(forms.Form): 
    MODELS = (
              ("Inversion",u"Inversión"),
              ("Ingreso",u"Ingreso"),
              ("Gasto",u"Gasto")    
              )
    periodo = forms.ChoiceField(choices= PERIODO_CHOICES,
                                       widget= forms.ChoiceField.widget(
                                    attrs={'class':"form-control required"},
                                    ),
                             required = True
                              )    
    year = forms.IntegerField(label=u"Año",
                              widget= forms.IntegerField.widget(
                                    attrs={'class':"form-control required"},
                                    ),
                              initial=lambda: datetime.date.today().year,
                             required = True
                              )
    municipio = forms.ModelChoiceField(queryset=Municipio.objects.all(),
                                       widget= forms.ModelChoiceField.widget(
                                    attrs={'class':"form-control required"},
                                    ),
                             required = True
                                       )
    tipo = forms.ChoiceField(choices= MODELS,
                                       widget= forms.ChoiceField.widget(
                                    attrs={'class':"form-control required"},
                                    ),
                             required = True
                              )
