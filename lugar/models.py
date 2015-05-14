from django.db import models
from autoslug import AutoSlugField
from pixelfields_smart_selects.db_fields import ChainedForeignKey

# Create your models here
#la clasificacion de un municipio(A,B,C) se determina en base a un promedio en los ingresos
class ClasificacionMunic(models.Model):
    #clasificacion = models.CharField()
    clasificacion = models.CharField(max_length=120) # FIXME 120???
    fecha_desde = models.DateField(null=False)
    fecha_hasta = models.DateField(null=False)
    desde = models.DecimalField('Desde', max_digits=12, decimal_places=2, blank=True, null=True)
    hasta = models.DecimalField('Hasta', max_digits=12, decimal_places=2, blank=True, null=True)
    color = models.CharField(max_length=30, null=True)

    class Meta:
        ordering = ['clasificacion']
    def __unicode__(self):
        return self.clasificacion

class Departamento(models.Model):
    nombre = models.CharField(max_length=120)
    slug = AutoSlugField(populate_from='nombre')
    latitud  = models.DecimalField('Latitud', max_digits=10, decimal_places=5, blank=True, null=True)
    longitud = models.DecimalField('Longitud', max_digits=10, decimal_places=5, blank=True, null=True)

    class Meta:
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre

class Municipio(models.Model):
    nombre = models.CharField(max_length=120)
    depto = models.ForeignKey(Departamento, related_name='departamento')
    slug = AutoSlugField(populate_from='nombre')
    latitud  = models.DecimalField('Latitud', max_digits=10, decimal_places=6, blank=True, null=True)
    longitud = models.DecimalField('Longitud', max_digits=10, decimal_places=6, blank=True, null=True)

    #class Meta:
    #    ordering = [u'nombre']
    def __unicode__(self):
        return self.nombre

class Comarca(models.Model):
    nombre = models.CharField(max_length=120)
    #municipio = models.ForeignKey(Municipio)
    slug = AutoSlugField(populate_from='nombre')
    departamento = models.ForeignKey(Departamento)
    municipio = ChainedForeignKey(Municipio,chained_field='departamento',chained_model_field='depto', null=True, blank=True)
    poblacion = models.IntegerField()
    latitud  = models.DecimalField('Latitud', max_digits=10, decimal_places=6, blank=True, null=True)
    longitud = models.DecimalField('Longitud', max_digits=10, decimal_places=6, blank=True, null=True)

    class Meta:
        ordering = ['nombre']
    def __unicode__(self):
        return self.nombre

class Poblacion(models.Model):
    municipio = models.ForeignKey(Municipio)
    anio = models.IntegerField()
    poblacion = models.IntegerField()

    class Meta:
        ordering = ['anio']
