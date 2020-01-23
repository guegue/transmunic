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
    minimo_inversion = models.IntegerField(null=True)
    color = models.CharField(max_length=30, null=True)

    class Meta:
        ordering = ['clasificacion']

    def __unicode__(self):
        return self.clasificacion


class Departamento(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    slug = AutoSlugField(populate_from='nombre', unique=True)
    codigo = models.CharField('Codigo', max_length=15, blank=True)
    latitud = models.DecimalField('Latitud', max_digits=10, decimal_places=5, blank=True, null=True)
    longitud = models.DecimalField('Longitud', max_digits=10,
                                   decimal_places=5, blank=True, null=True)

    class Meta:
        ordering = ['nombre']

    def __unicode__(self):
        return self.nombre


class MunicipioQuerySet(models.QuerySet):
    def for_user(self, user):
        if hasattr(user, 'profile') and user.profile.municipio:
            return self.filter(id=user.profile.municipio.id)
        return self


class Municipio(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    depto = models.ForeignKey(Departamento, related_name='departamento')
    slug = AutoSlugField(populate_from='nombre', verbose_name="municipio", unique=True)
    latitud = models.DecimalField('Latitud', max_digits=10, decimal_places=6, blank=True, null=True)
    longitud = models.DecimalField('Longitud', max_digits=10,
                                   decimal_places=6, blank=True, null=True)
    clasificaciones = models.ManyToManyField(ClasificacionMunic, through='ClasificacionMunicAno')

    objects = MunicipioQuerySet.as_manager()

    class Meta:
        ordering = [u'nombre']

    def __unicode__(self):
        return self.nombre

class ClasificacionMunicAno(models.Model):
    municipio = models.ForeignKey(Municipio, related_name="clase")
    clasificacion = models.ForeignKey(ClasificacionMunic, related_name="clase")
    anio = models.IntegerField()

    class Meta:
        unique_together = ('municipio', 'anio')


class Comarca(models.Model):
    nombre = models.CharField(max_length=120)
    #municipio = models.ForeignKey(Municipio)
    slug = AutoSlugField(populate_from='nombre')
    departamento = models.ForeignKey(Departamento)
    municipio = ChainedForeignKey(Municipio, chained_field='departamento',
                                  chained_model_field='depto', null=True, blank=True)
    poblacion = models.IntegerField()
    latitud = models.DecimalField('Latitud', max_digits=10, decimal_places=6, blank=True, null=True)
    longitud = models.DecimalField('Longitud', max_digits=10,
                                   decimal_places=6, blank=True, null=True)

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


class Periodo(models.Model):
    desde = models.IntegerField(null=False, verbose_name=u'Desde')
    hasta = models.IntegerField(null=False, verbose_name=u'Hasta')

    class Meta:
        ordering = ['desde']

class PeriodoMunic(models.Model):
    municipio = models.ForeignKey(Municipio)
    periodo = models.ForeignKey(Periodo)
    partido = models.CharField(max_length=30, null=True)

    class Meta:
        ordering = ['periodo']
