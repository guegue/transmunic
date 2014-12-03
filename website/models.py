# -*- coding:utf-8 -*-
from django.db import models
from django.contrib.flatpages.models import FlatPage
from sorl.thumbnail import ImageField

class Departamento(models.Model):
    nombre = models.CharField(max_length=120)
    slug = models.SlugField(max_length=60)
    latitud  = models.DecimalField('Latitud', max_digits=10, decimal_places=5, blank=True, null=True)
    longitud = models.DecimalField('Longitud', max_digits=10, decimal_places=5, blank=True, null=True)

    class Meta:
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre

class Municipio(models.Model):
    nombre = models.CharField(max_length=120)
    depto = models.ForeignKey(Departamento, related_name='departamento')
    slug = models.SlugField(max_length=60)
    poblacion = models.IntegerField()
    latitud  = models.DecimalField('Latitud', max_digits=10, decimal_places=6, blank=True, null=True)
    longitud = models.DecimalField('Longitud', max_digits=10, decimal_places=6, blank=True, null=True)

    class Meta:
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre

class Comarca(models.Model):
    nombre = models.CharField(max_length=120)
    municipio = models.ForeignKey(Municipio)
    slug = models.SlugField(max_length=60)
    poblacion = models.IntegerField()
    latitud  = models.DecimalField('Latitud', max_digits=10, decimal_places=6, blank=True, null=True)
    longitud = models.DecimalField('Longitud', max_digits=10, decimal_places=6, blank=True, null=True)

    class Meta:
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre

class CatInversion(models.Model):
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=80)

    class Meta:
        verbose_name_plural = 'Categorias de inversion'
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre
 
class TipoGasto(models.Model):
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=80)
 
    class Meta:
        verbose_name_plural = 'Tipo de gastos'
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre

class SubTipoGasto(models.Model):
    tipogasto = models.ForeignKey(TipoGasto, related_name='tipo')
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=80)
 
    class Meta:
        verbose_name_plural = 'Sub-Tipo de gastos'
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre

class OrigenRecurso(models.Model):
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=80)

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
    slug = models.SlugField(max_length=50)
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
    slug = models.SlugField(max_length=80)
 
    class Meta:
        verbose_name_plural = 'Subtipos de ingresos'
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre

class SubSubTipoIngreso(models.Model):
    subtipoingreso = models.ForeignKey(SubTipoIngreso, related_name='tipo')
    nombre = models.CharField(max_length=250)
    slug = models.SlugField(max_length=80)
 
    class Meta:
        verbose_name_plural = 'Sub-subtipos de ingresos'
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre

class FuenteFmto(models.Model):
    nombre = models.CharField(max_length=250)
    slug = models.SlugField(max_length=80)

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

class Banner(models.Model):
    municipio = models.ForeignKey(Municipio)
    titulo = models.CharField(max_length=200)
    imagen = ImageField(upload_to='banner', verbose_name='Banner')
    descripcion = models.CharField(max_length=500, null=True, blank=True)
    enlace = models.CharField(max_length=200, null=True, blank=True)
    orden = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['orden']
    def __unicode__(self):
        return self.titulo

class Donante(models.Model):
    nombre = models.CharField(max_length=200)
    logo = ImageField(upload_to='donante', verbose_name='Logotipo')
    descripcion = models.CharField(max_length=500, null=True, blank=True)
    enlace = models.CharField(max_length=200, null=True, blank=True)

    def __unicode__(self):
        return self.nombre

class TipoProyecto(models.Model):
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=80)
 
    class Meta:
        verbose_name_plural = 'Tipo de proyectos'
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre
