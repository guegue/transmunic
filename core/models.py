
from django.conf import settings
from django.db import models
from website.models import *

# Ingresos del municipio
class Ingreso(models.Model):
    anio = models.IntegerField(null=False)
    municipio = models.ForeignKey(Municipio)
    subsubtipoingreso = models.ForeignKey(SubSubTipoIngreso)
    descripcion = models.TextField(blank=True,null=True)

    class Meta:
        verbose_name_plural = 'Ingresos'
    def __unicode__(self):
        return self.anio


class IngresoDetalle(models.Model):
    ingreso = models.ForeignKey(Ingreso)
    fecha = models.DateField(null=False)
    monto = models.DecimalField(max_digits=12, decimal_places=6, blank=False, null=False)
    ejecutado = models.DecimalField(max_digits=12, decimal_places=6, blank=False, null=False)
    donante = models.ForeignKey(Donante)

    class Meta:
        verbose_name_plural = 'Detalle de Ingresos'
    def __unicode__(self):
        return self.fecha

class Gasto(models.Model):
    GASTO = 0
    INVERSION = 1
    TIPO_CHOICES = (
        (GASTO, 'Gasto'),
        (INVERSION, 'Inversion'),
    )
    tipo = models.IntegerField(choices=TIPO_CHOICES, default=0)
    fecha = models.DateField(null=True)
    origen = models.ForeignKey(SubSubTipoIngreso)
    monto = models.DecimalField(max_digits=12, decimal_places=6, blank=True, null=True)
    municipio = models.ForeignKey(Municipio)
    comarca = models.ForeignKey(Comarca)
    subtipogasto = models.ForeignKey(TipoGasto)
    catinversion = models.ForeignKey(CatInversion)
    areageografica = models.ForeignKey(AreaGeografica)
    descripcion = models.TextField(blank=True,null=True)

    class Meta:
        verbose_name_plural = 'Gastos/Inversion'
        ordering = ['fecha']
    def __unicode__(self):
        return self.fecha

#Fuente de financiamiento
class GastoFuenteFmto(models.Model):
    gasto = models.ForeignKey(Gasto)
    fuentefmto = models.ForeignKey(FuenteFmto)

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
    financiamiento = models.DecimalField(max_digits=12, decimal_places=6)
    fecha = models.DateField(null=True)

    class Meta:
        verbose_name_plural = 'Proyecto detalle'
    def __unicode__(self):
        return self.proyecto


