# -*- coding: utf-8 -*-

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Sum, Max, Min

from autoslug import AutoSlugField
from sorl.thumbnail import ImageField
from pixelfields_smart_selects.db_fields import ChainedForeignKey

from lugar.models import *

PERIODO_INICIAL = 'I'
PERIODO_ACTUALIZADO = 'A'
PERIODO_FINAL = 'F'
# FIXME : ' P. Inicial' (leading space needed to be first)
PERIODO_VERBOSE = {'I': 'P. Inicial', 'A': 'Actualizado', 'F': 'Ejecutado'}
PERIODO_CHOICES = (
    (PERIODO_INICIAL, 'Inicial'),
    (PERIODO_ACTUALIZADO, 'Actualizado'),
    (PERIODO_FINAL, 'Final'),
)
AREAGEOGRAFICA_VERBOSE = {'R': 'Rural', 'U': 'Urbana', 'M': 'Eme?', 'O': 'Otros', '': 'Vacio', None: 'None'}
CLASIFICACION_VERBOSE = {0: 'Corriente', 1: 'Capital', None: 'None'}

class Organizacion(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True,null=True)
    correo = models.CharField(max_length=100, null=True, blank=True)
    web = models.CharField(max_length=200, null=True, blank=True)
    logo = ImageField(upload_to='organizacion', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Organizaciones'
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre

class Grafico(models.Model):
    id = models.CharField(max_length=25,  primary_key=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True,null=True)
    notas = models.TextField(blank=True,null=True)
    imagen_objetivo = ImageField(upload_to='grafico',null=True,blank=True)
    imagen_actual = ImageField(upload_to='grafico',null=True,blank=True)

    class Meta:
        verbose_name_plural = 'Graficos'
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre

class Anio(models.Model):
    anio = models.IntegerField()
    periodo = models.CharField(max_length=1)
    inicial = models.DateField(null=True, blank=True)
    actualizado = models.DateField(null=True, blank=True)
    final = models.DateField(null=True, blank=True)
    def __unicode__(self):
        return u'%s %s' % (self.anio, self.periodo)

class CatInversion(models.Model):
    nombre = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='nombre')
    minimo = models.DecimalField(max_digits=5, decimal_places=2, null=True,blank=True)
    destacar = models.BooleanField()

    class Meta:
        verbose_name_plural = 'Categorias de inversion'
        verbose_name = 'Categoria de inversion'
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre

class OrigenGasto(models.Model):
    nombre = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='nombre')

    class Meta:
        verbose_name_plural = 'Origen  de los gastos'
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre

class TipoGasto(models.Model):
    PERSONAL = '1000000'
    PERSONAL_PERMANENTE = '1100000'
    IMPREVISTOS = '9000000'
    TRANSFERENCIAS_CAPITAL = '6000000'
    CORRIENTE = '0'
    CAPITAL = '1'
    CLASIFICACION_CHOICES = (
        (CORRIENTE, 'Gasto Corriente'),
        (CAPITAL, 'Gasto de Capital'),
    )
    codigo = models.CharField(max_length=25,  primary_key=True)
    nombre = models.CharField(max_length=200, )
    slug = AutoSlugField(populate_from='nombre', null=True)
    clasificacion = models.IntegerField(choices=CLASIFICACION_CHOICES, default=0, null=True)

    class Meta:
        verbose_name_plural = 'Tipo de gastos'
        ordering = ['codigo']
    def __unicode__(self):
        return self.nombre

class SubTipoGasto(models.Model):
    codigo = models.CharField(max_length=25,  primary_key=True)
    tipogasto = models.ForeignKey(TipoGasto, related_name='tipo')
    nombre = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='nombre')

    class Meta:
        verbose_name_plural = 'Sub-Tipo de gastos'
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre

class SubSubTipoGasto(models.Model):
    codigo = models.CharField(max_length=25,  primary_key=True)
    subtipogasto = models.ForeignKey(SubTipoGasto, related_name='subtipo')
    nombre = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='nombre')
    origen = models.ForeignKey(OrigenGasto, related_name='origen', null=True)

    class Meta:
        verbose_name_plural = 'Sub-Sub-Tipo de gastos'
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre

class OrigenRecurso(models.Model):
    # FIXME: id es auto!!! RECAUDACION puede no ser == 1
    RECAUDACION = 1
    nombre = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='nombre')

    class Meta:
        verbose_name_plural = 'Origen  de los recursos'
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre

class TipoIngreso(models.Model):
    TRANSFERENCIAS_CORRIENTES = '15000000'
    CORRIENTE = 0
    CAPITAL = 1
    CLASIFICACION_CHOICES = (
        (CORRIENTE, 'Ingreso Corriente'),
        (CAPITAL, 'Ingreso Capital'),
    )
    codigo = models.CharField(max_length=25,  primary_key=True)
    nombre = models.CharField(max_length=200, )
    slug = AutoSlugField(populate_from='nombre', null=True)
    #si no es ingreso corriente, entonces es de Capital
    clasificacion = models.IntegerField(choices=CLASIFICACION_CHOICES, default=0, null=True)

    class Meta:
        verbose_name_plural = 'Tipo de ingreso'
        ordering = ['codigo']
    def __unicode__(self):
        return self.nombre

class SubTipoIngreso(models.Model):
    codigo = models.CharField(max_length=25,  primary_key=True)
    tipoingreso = models.ForeignKey(TipoIngreso, related_name='tipo')
    nombre = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='nombre')

    class Meta:
        verbose_name_plural = 'Subtipos de ingresos'
        ordering = ['codigo']
    def __unicode__(self):
        return self.nombre

class SubSubTipoIngreso(models.Model):
    codigo = models.CharField(max_length=25,  primary_key=True)
    subtipoingreso = models.ForeignKey(SubTipoIngreso, related_name='subtipo')
    nombre = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='nombre')
    origen = models.ForeignKey(OrigenRecurso, related_name='origen', null=True)

    class Meta:
        verbose_name_plural = 'Sub-subtipos de ingresos'
        ordering = ['codigo']
    def __unicode__(self):
        return self.nombre

# Ingresos del municipio
class Ingreso(models.Model):
    fecha = models.DateField(null=False)
    anio = models.IntegerField(null=False, verbose_name=u'Año')
    periodo = models.CharField(max_length=1, null=False)
    departamento = models.ForeignKey(Departamento)
    municipio = ChainedForeignKey(Municipio,chained_field='departamento',chained_model_field='depto', null=True, blank=True)
    descripcion = models.TextField(blank=True,null=True)

    class Meta:
        verbose_name_plural = 'Ingresos'

    #def __unicode__(self):
    #    return self.ingreso


class IngresoDetalle(models.Model):
    ingreso = models.ForeignKey(Ingreso)
    codigo = models.CharField(max_length=15, null=False)
    tipoingreso = models.ForeignKey(TipoIngreso)
    subtipoingreso = ChainedForeignKey(SubTipoIngreso,chained_field='tipoingreso',chained_model_field='tipoingreso', null=True, blank=True)
    subsubtipoingreso = ChainedForeignKey(SubSubTipoIngreso,chained_field='subtipoingreso',chained_model_field='subtipoingreso', null=True, blank=True)
    cuenta = models.CharField(max_length=400, null=False)
    asignado = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    ejecutado = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False)

    class Meta:
        verbose_name_plural = 'Detalle de ingresos'
        ordering = ['ingreso']
    def __unicode__(self):
        return self.codigo

class Gasto(models.Model):
    fecha = models.DateField(null=False)
    anio = models.IntegerField(null=False, verbose_name=u'Año')
    periodo = models.CharField(max_length=1, null=False)
    departamento = models.ForeignKey(Departamento)
    municipio = ChainedForeignKey(Municipio,chained_field='departamento',chained_model_field='depto', null=True, blank=True)
    descripcion = models.TextField(blank=True,null=True)

    class Meta:
        verbose_name_plural = 'Gastos'
        ordering = ['fecha']

#detalle del gasto
class GastoDetalle(models.Model):
    gasto = models.ForeignKey(Gasto)
    codigo = models.CharField(max_length=15, null=False)
    tipogasto = models.ForeignKey(TipoGasto)
    subtipogasto = ChainedForeignKey(SubTipoGasto,chained_field='tipogasto',chained_model_field='tipogasto', null=True, blank=True)
    subsubtipogasto = ChainedForeignKey(SubSubTipoGasto,chained_field='subtipogasto',chained_model_field='subtipogasto', null=True, blank=True)
    cuenta = models.CharField(max_length=400, null=False)
    asignado = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    ejecutado = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False)

    class Meta:
        verbose_name_plural = 'Detalle de gastos'
        ordering = ['gasto']
    def __unicode__(self):
        return self.codigo

class TipoProyecto(models.Model):
    nombre = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='nombre')

    class Meta:
        verbose_name_plural = 'Tipo de proyectos'
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre

class Inversion(models.Model):
    departamento = models.ForeignKey(Departamento, null=True)
    #municipio = ChainedForeignKey(Municipio,chained_field='departamento',chained_model_field='depto', null=True, blank=True)
    municipio = models.ForeignKey(Municipio, null=True, blank=True)
    nombremunic = models.CharField(max_length=250, null=True,blank=True)
    fecha = models.DateField(null=False)
    anio = models.IntegerField(null=False, verbose_name=u'Año')
    periodo = models.CharField(max_length=1, null=False)

    class Meta:
        verbose_name_plural = 'Inversion'

class Proyecto(models.Model):
    URBANA = 'U'
    RURAL = 'R'
    OTROS = 'O'
    AREA_CHOICES = (
        (URBANA, 'Urbana'),
        (RURAL, 'Rural'),
        (OTROS, 'Otros'),
    )
    inversion = models.ForeignKey(Inversion, related_name='inversion', null=True)
    codigo = models.CharField(max_length=20, null=True)
    nombre = models.CharField(max_length=500)
    tipoproyecto = models.ForeignKey(TipoProyecto, related_name='tipo_proyecto', null=True,blank=True)
    catinversion = models.ForeignKey(CatInversion, related_name='categoria_inversion', null=True,blank=True)
    areageografica = models.CharField(choices=AREA_CHOICES, max_length=1, null=True, blank=True)
    asignado = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    ejecutado = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False)
    ficha =  models.FileField(upload_to='proyecto', blank=True, null=True)

    @property
    def porcentaje_ejecutado(self):
        if self.asignado > 0 and self.ejecutado > 0:
            return round(self.ejecutado / self.asignado * 100, 2)
        else:
            return None

    @property
    def areageografica_verbose(self):
        return self.areageografica

    class Meta:
        verbose_name_plural = 'Proyectos'
    def __unicode__(self):
        return self.nombre

#financiamiento
class TipoFuenteFmto(models.Model):
    nombre = models.CharField(max_length=250)
    slug = AutoSlugField(populate_from='nombre')

    class Meta:
        verbose_name_plural = 'Tipos de Fuentes de financiamiento'
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre

class FuenteFmto(models.Model):
    nombre = models.CharField(max_length=250)
    slug = AutoSlugField(populate_from='nombre')
    tipofuente = models.ForeignKey(TipoFuenteFmto)

    class Meta:
        verbose_name_plural = 'Fuentes de financiamiento'
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre

# Ingresos del municipio
class InversionFuente(models.Model):
    fecha = models.DateField(null=False)
    anio = models.IntegerField(null=False, verbose_name=u'Año')
    periodo = models.CharField(max_length=1, null=False)
    departamento = models.ForeignKey(Departamento)
    municipio = ChainedForeignKey(Municipio,chained_field='departamento',chained_model_field='depto', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Inversion de fuentes de financiamiento'

class InversionFuenteDetalle(models.Model):
    inversionfuente = models.ForeignKey(InversionFuente)
    tipofuente = models.ForeignKey(TipoFuenteFmto)
    fuente = ChainedForeignKey(FuenteFmto,chained_field='tipofuente',chained_model_field='tipofuente', null=True, blank=True)
    asignado = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    ejecutado = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False)

    class Meta:
        verbose_name_plural = 'Detalle de inversion por fuente'
        ordering = ['inversionfuente']
