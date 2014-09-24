# -*- coding:utf-8 -*-
from django.db import models

class CategoriaInversion(models.Model):
    nombre = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = 'Categoria Inversion'
 
class OrigenRecursos(models.Model):
    nombre = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = 'Origen Recursos'

class FuenteFmto(models.Model):
    nombre = models.CharField(max_length=30)
    origen_recurso = models.ForeignKey(OrigenRecursos, related_name="origen")

    class Meta:
        verbose_name_plural = 'Fuente Financiamiento'

class Municipio(models.Model):
    nombre = models.CharField(max_length=30)
    poblacion = models.IntegerField()
    latitud  = models.DecimalField('Latitud', max_digits=8, decimal_places=5, blank=True, null=True)
    longitud = models.DecimalField('Longitud', max_digits=8, decimal_places=5, blank=True, null=True)

class Ingresos(models.Model):
    municipio = models.ForeignKey(Municipio, related_name="municipio_ingreso") 
    financiamiento = models.ForeignKey(FuenteFmto, related_name="fmto_ingreso")

    class Meta:
        verbose_name_plural = 'Ingresos'

class Area(models.Model):
    nombre = models.CharField(max_length=30)

class TipoGastos(models.Model):
    nombre = models.CharField(max_length=30)
 
    class Meta:
        verbose_name_plural = 'Tipo Gastos'

class Gastos(models.Model):
    municipio = models.ForeignKey(Municipio, related_name="municipio_gasto")
    area = models.ForeignKey(Area, related_name="area_gasto")
    financiamieno = models.ForeignKey(FuenteFmto, related_name="fmto_gasto")
    tipo_gasto = models.ForeignKey(TipoGastos, related_name="tipo_gasto")

    class Meta:
        verbose_name_plural = 'Gastos'

class Inversion(models.Model):
    municipio = models.ForeignKey(Municipio, related_name="municipio_inversion")
    area = models.ForeignKey(Area, related_name="area_inversion")
    categoria_inv = models.ForeignKey(CategoriaInversion, related_name="categoria")
    financiamiento = models.ForeignKey(FuenteFmto, related_name="fmto_inv")


    class Meta:
        verbose_name_plural = 'Inversion'

