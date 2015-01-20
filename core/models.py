from django.conf import settings
from django.db import models
from decimal import Decimal
from lugar.models import *
from autoslug import AutoSlugField
from pixelfields_smart_selects.db_fields import ChainedForeignKey

class CatInversion(models.Model):
    nombre = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='nombre')

    class Meta:
        verbose_name_plural = 'Categorias de inversion'
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre
 
class TipoGasto(models.Model):
    codigo = models.CharField(max_length=25,  primary_key=True)
    nombre = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='nombre')
 
    class Meta:
        verbose_name_plural = 'Tipo de gastos'
        ordering = ['nombre']
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
 
    class Meta:
        verbose_name_plural = 'Sub-Sub-Tipo de gastos'
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre

class OrigenRecurso(models.Model):
    nombre = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='nombre')

    class Meta:
        verbose_name_plural = 'Origen  de los recursos'
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre

class TipoIngreso(models.Model):
    CORRIENTE = 0
    CAPITAL = 1
    CLASIFICACION_CHOICES = (
        (CORRIENTE, 'Ingreso Corriente'),
        (CAPITAL, 'Ingreso Capital'),
    )
    nombre = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='nombre')
    #si no es ingreso corriente, entonces es de Capital
    clasificacion = models.IntegerField(choices=CLASIFICACION_CHOICES, default=0)
 
    class Meta:
        verbose_name_plural = 'Tipo de ingreso'
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre

class SubTipoIngreso(models.Model):
    tipoingreso = models.ForeignKey(TipoIngreso, related_name='tipo')
    nombre = models.CharField(max_length=250)
    slug = AutoSlugField(populate_from='nombre')

    class Meta:
        verbose_name_plural = 'Subtipos de ingresos'
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre

class SubSubTipoIngreso(models.Model):
    subtipoingreso = models.ForeignKey(SubTipoIngreso, related_name='tipo')
    nombre = models.CharField(max_length=250)
    slug = AutoSlugField(populate_from='nombre')
 
    class Meta:
        verbose_name_plural = 'Sub-subtipos de ingresos'
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre

class FuenteFmto(models.Model):
    nombre = models.CharField(max_length=250)
    slug = AutoSlugField(populate_from='nombre')

    class Meta:
        verbose_name_plural = 'Fuentes de financiamiento'
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre

class AreaGeografica(models.Model):
    nombre = models.CharField(max_length=50)
    slug = models.SlugField(max_length=30)

    class Meta:
        verbose_name_plural = 'Area geografica'
    def __unicode__(self):
        return self.nombre

class Donante(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.CharField(max_length=500, null=True, blank=True)
    enlace = models.CharField(max_length=200, null=True, blank=True)

    def __unicode__(self):
        return self.nombre

class TipoProyecto(models.Model):
    nombre = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='nombre')
 
    class Meta:
        verbose_name_plural = 'Tipo de proyectos'
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre

# Ingresos del municipio
class Ingreso(models.Model):
    fecha = models.DateField(null=False)
    departamento = models.ForeignKey(Departamento)
    municipio = ChainedForeignKey(Municipio,chained_field='departamento',chained_model_field='depto', null=True, blank=True)
    descripcion = models.TextField(blank=True,null=True)

    class Meta:
        verbose_name_plural = 'Ingresos'
    #def __unicode__(self):
    #    return self.ingreso

class IngresoDetalle(models.Model):
    ingreso = models.ForeignKey(Ingreso)
    fecha = models.DateField(null=False)
    titulo = models.CharField(max_length=450)
    tipoingreso = models.ForeignKey(TipoIngreso)
    subtipoingreso = ChainedForeignKey(SubTipoIngreso,chained_field='tipoingreso',chained_model_field='tipoingreso', null=True, blank=True)
    subsubtipoingreso = ChainedForeignKey(SubSubTipoIngreso,chained_field='subtipoingreso',chained_model_field='subtipoingreso', null=True, blank=True)
    monto = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False)
    ejecutado = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False)
    donante = models.ForeignKey(Donante,blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Detalle de Ingresos'
    #def __unicode__(self):
    #    return self.fecha

class Gasto(models.Model):
    fecha = models.DateField(null=False)
    departamento = models.ForeignKey(Departamento)
    municipio = ChainedForeignKey(Municipio,chained_field='departamento',chained_model_field='depto', null=True, blank=True)
    descripcion = models.TextField(blank=True,null=True)

    class Meta:
        verbose_name_plural = 'Gastos'
        ordering = ['fecha']
    def __unicode__(self):
        return self.fecha

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


class Proyecto(models.Model):
    M2 = 0
    KM = 1
    MZ = 2
    UNIDAD = 3
    UNIDAD_CHOICES = (
        (M2, 'm2'),
        (KM, 'Km'),
        (MZ, 'Mz'),
        (UNIDAD, 'Unidad'),
    )
    municipio = models.ForeignKey(Municipio, related_name='nombre_municipio')
    comarca = models.ForeignKey(Comarca)
    codigo = models.CharField(max_length=20)
    nombre = models.CharField(max_length=200)
    fecha_ini = models.DateField(null=True)
    fecha_fin = models.DateField(null=True)
    tipoproyecto = models.ForeignKey(TipoProyecto, related_name='tipo_proyecto')
    catinversion = models.ForeignKey(CatInversion, related_name='categoria_inversion')
    areageografica = models.ForeignKey(AreaGeografica, related_name='area_geografica')
    fisico = models.CharField(max_length=80) 
    um = models.IntegerField('U.M', choices=UNIDAD_CHOICES, default=0) #unidad de medida
    descripcion = models.TextField(blank=True,null=True)

    class Meta:
        verbose_name_plural = 'Proyectos'
    def __unicode__(self):
        return self.nombre

class ProyectoDetalle(models.Model):
    proyecto = models.ForeignKey(Proyecto)
    financiamiento = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField(null=True)

    class Meta:
        verbose_name_plural = 'Proyecto detalle'
    def __unicode__(self):
        return self.proyecto


