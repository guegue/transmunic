# -*- coding: utf-8 -*-

from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Sum, Max, Min

from autoslug import AutoSlugField
from sorl.thumbnail import ImageField
from pixelfields_smart_selects.db_fields import ChainedForeignKey
from django.utils.encoding import python_2_unicode_compatible

from lugar.models import Municipio, Departamento

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
AREAGEOGRAFICA_VERBOSE = {
    'R': 'Rural',
    'U': 'Urbana',
    'M': 'Eme?',
    'O': 'Otros',
    '': 'Vacio',
    None: 'None'}
CLASIFICACION_VERBOSE = {0: 'Corriente', 1: 'Capital', None: 'None'}


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    municipio = models.ForeignKey(Municipio, null=True, blank=True)

    class Meta:
        verbose_name = u'Perfil'
        verbose_name_plural = u'Perfiles'
        ordering = ['user']

    def __unicode__(self):
        return self.user.username


class Organizacion(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    correo = models.CharField(max_length=100, null=True, blank=True)
    web = models.CharField(max_length=200, null=True, blank=True)
    logo = ImageField(upload_to='organizacion', null=True, blank=True)

    class Meta:
        verbose_name_plural = u'Organizaciones'
        verbose_name = u'Organización'
        ordering = ['nombre']

    def __unicode__(self):
        return self.nombre


class Grafico(models.Model):
    id = models.CharField(max_length=25,  primary_key=True)
    nombre = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    imagen_objetivo = ImageField(upload_to='grafico', null=True, blank=True)
    imagen_actual = ImageField(upload_to='grafico', null=True, blank=True)

    class Meta:
        verbose_name = u'Gráfico'
        ordering = ['nombre']

    def __unicode__(self):
        return self.nombre


class Anio(models.Model):
    anio = models.IntegerField(unique=True)
    periodo = models.CharField(max_length=1)
    inicial = models.DateField(null=True, blank=True)
    actualizado = models.DateField(null=True, blank=True)
    final = models.DateField(null=True, blank=True)
    mapping = JSONField()

    class Meta:
        verbose_name = u'Año'

    def __unicode__(self):
        return u'%s %s' % (self.anio, self.periodo)


class CatInversion(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=80)
    minimo = models.DecimalField(max_digits=5, decimal_places=2, null=True,
                                 blank=True)
    destacar = models.BooleanField(default=False)
    color = models.CharField(max_length=8, default="#2b7ab3")
    shortname = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        verbose_name_plural = u'Categorías de inversión'
        verbose_name = u'Categoría de inversión'
        ordering = ['nombre']

    def __unicode__(self):
        return self.nombre


class OrigenGasto(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    slug = AutoSlugField(populate_from='nombre')
    shortname = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Origenes de los gastos'
        verbose_name = 'Origen de los gastos'
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
    codigo = models.CharField(max_length=25, primary_key=True)
    nombre = models.CharField(max_length=200, )
    slug = AutoSlugField(populate_from='nombre', null=True)
    shortname = models.CharField(max_length=25, blank=True, null=True)
    clasificacion = models.IntegerField(
        choices=CLASIFICACION_CHOICES,
        default=0, null=True)

    class Meta:
        verbose_name_plural = 'Tipos de gastos'
        verbose_name = 'Tipo de gastos'
        ordering = ['codigo']

    def __unicode__(self):
        return self.nombre


class SubTipoGasto(models.Model):
    codigo = models.CharField(max_length=25,  primary_key=True)
    tipogasto = models.ForeignKey(TipoGasto, related_name='tipo')
    nombre = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='nombre')
    shortname = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Sub tipos de gastos'
        verbose_name = 'Sub tipo de gastos'
        ordering = ['nombre']

    def __unicode__(self):
        return self.nombre


class SubSubTipoGasto(models.Model):
    codigo = models.CharField(max_length=25,  primary_key=True)
    subtipogasto = models.ForeignKey(SubTipoGasto, related_name='subtipo')
    nombre = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='nombre')
    shortname = models.CharField(max_length=25, blank=True, null=True)
    origen = models.ForeignKey(OrigenGasto, related_name='origen', null=True)

    class Meta:
        verbose_name_plural = 'Sub sub tipos de gastos'
        verbose_name = 'Sub sub tipo de gastos'
        ordering = ['nombre']

    def __unicode__(self):
        return self.nombre


class OrigenRecurso(models.Model):
    # FIXME: id es auto!!! RECAUDACION puede no ser == 1
    RECAUDACION = 1
    nombre = models.CharField(max_length=200, unique=True)
    slug = AutoSlugField(populate_from='nombre')
    shortname = models.CharField(max_length=25, blank=True, null=True, unique=True)

    class Meta:
        verbose_name_plural = 'Origenes de los recursos'
        verbose_name = 'Origen de los recursos'
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
    shortname = models.CharField(max_length=25, blank=True, null=True)
    # si no es ingreso corriente, entonces es de Capital
    clasificacion = models.IntegerField(
        choices=CLASIFICACION_CHOICES, default=0, null=True)

    class Meta:
        verbose_name_plural = 'Tipos de ingreso'
        verbose_name = 'Tipo de ingreso'
        ordering = ['codigo']

    def __unicode__(self):
        return self.nombre


class SubTipoIngreso(models.Model):
    codigo = models.CharField(max_length=25,  primary_key=True)
    tipoingreso = models.ForeignKey(TipoIngreso, related_name='tipo')
    nombre = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='nombre')
    shortname = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Subtipos de ingreso'
        verbose_name = 'Subtipo de ingreso'
        ordering = ['codigo']

    def __unicode__(self):
        return self.nombre


class SubSubTipoIngreso(models.Model):
    codigo = models.CharField(max_length=25,  primary_key=True)
    subtipoingreso = models.ForeignKey(SubTipoIngreso, related_name='subtipo')
    nombre = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='nombre')
    shortname = models.CharField(max_length=25, blank=True, null=True)
    origen = models.ForeignKey(OrigenRecurso, related_name='origen', null=True)

    class Meta:
        verbose_name_plural = 'Sub-subtipos de ingreso'
        verbose_name = 'Sub-subtipo de ingreso'
        ordering = ['codigo']

    def __unicode__(self):
        return self.nombre


class Sub3TipoIngreso(models.Model):
    codigo = models.CharField(max_length=25,  primary_key=True)
    subsubtipoingreso = models.ForeignKey(SubSubTipoIngreso, related_name='subsubtipo')
    nombre = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='nombre')
    shortname = models.CharField(max_length=25, blank=True, null=True)
    origen = models.ForeignKey(OrigenRecurso, related_name='origen_recurso', null=True)

    class Meta:
        verbose_name_plural = 'Sub3 Tipo de ingreso'
        verbose_name = 'Sub3 Tipo de ingreso'
        ordering = ['codigo']

    def __unicode__(self):
        return self.nombre


# Ingresos del municipio
class IngresoRenglon(models.Model):
    codigo = models.CharField(max_length=25, primary_key=True)
    nombre = models.CharField(max_length=200)
    subsubtipoingreso = models.ForeignKey(SubSubTipoIngreso, null=True, blank=True)
    sub3tipoingreso = models.ForeignKey(Sub3TipoIngreso, null=True, blank=True)

    class Meta:
        verbose_name = u'Renglón Ingreso'
        ordering = ['subsubtipoingreso', 'codigo']

    def __unicode__(self):
        return u"{}: {}".format(self.codigo, self.nombre)


class Ingreso(models.Model):
    fecha = models.DateField(null=False)
    anio = models.IntegerField(null=False, verbose_name=u'Año')
    periodo = models.CharField(max_length=1, null=False)
    departamento = models.ForeignKey(Departamento)
    municipio = ChainedForeignKey(
        Municipio, chained_field='departamento',
        chained_model_field='depto')
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = [['anio', 'periodo', 'municipio']]
        ordering = ['anio', 'periodo', 'municipio']

    def __unicode__(self):
        return u"{}:{}:{}".format(self.anio, self.periodo, self.municipio)

    def save(self, *args, **kwargs):
        if not self.departamento_id and self.municipio_id:
            self.departamento_id = self.municipio.depto_id
        super(Ingreso, self).save(*args, **kwargs)


class IngresoDetalle(models.Model):
    ingreso = models.ForeignKey(Ingreso)
    codigo = models.ForeignKey(IngresoRenglon)
    tipoingreso = models.ForeignKey(TipoIngreso)
    subtipoingreso = ChainedForeignKey(
            SubTipoIngreso, chained_field='tipoingreso',
            chained_model_field='tipoingreso', null=True, blank=True)
    subsubtipoingreso = ChainedForeignKey(
            SubSubTipoIngreso, chained_field='subtipoingreso',
            chained_model_field='subtipoingreso', null=True, blank=True)
    sub3tipoingreso = models.ForeignKey(Sub3TipoIngreso, null=True, blank=True)
    cuenta = models.CharField(max_length=400, null=False)
    asignado = models.DecimalField(
            max_digits=12, decimal_places=2, blank=True, null=True)
    ejecutado = models.DecimalField(
            max_digits=12, decimal_places=2, blank=False, null=False)

    class Meta:
        unique_together = [['ingreso', 'codigo']]
        ordering = ['ingreso', 'codigo']
        verbose_name_plural = 'Detalles de ingresos'
        verbose_name = 'Detalle de ingresos'

    def __unicode__(self):
        return u"{}:{}:{}".format(self.id, self.codigo, self.cuenta)


# gastos del municipio
class Gasto(models.Model):
    fecha = models.DateField(null=False)
    anio = models.IntegerField(null=False, verbose_name=u'Año')
    periodo = models.CharField(max_length=1, null=False)
    departamento = models.ForeignKey(Departamento)
    municipio = ChainedForeignKey(
        Municipio, chained_field='departamento',
        chained_model_field='depto')
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = [['anio', 'periodo', 'municipio']]
        ordering = ['anio', 'periodo', 'municipio']

    def save(self, *args, **kwargs):
        if not self.departamento_id and self.municipio_id:
            self.departamento_id = self.municipio.depto_id
        super(Gasto, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"{}:{}:{}".format(self.anio, self.periodo, self.municipio)


class GastoRenglon(models.Model):
    codigo = models.CharField(max_length=25, primary_key=True)
    nombre = models.CharField(max_length=200)
    subsubtipogasto = models.ForeignKey(SubSubTipoGasto)

    class Meta:
        verbose_name = u'Renglón Gasto'
        ordering = ['subsubtipogasto', 'codigo']

    def __unicode__(self):
        return u"{}: {}".format(self.codigo, self.nombre)


class GastoDetalle(models.Model):
    gasto = models.ForeignKey(Gasto)
    codigo = models.ForeignKey(GastoRenglon)
    tipogasto = models.ForeignKey(TipoGasto)
    subtipogasto = ChainedForeignKey(
            SubTipoGasto, chained_field='tipogasto',
            chained_model_field='tipogasto', null=True, blank=True)
    subsubtipogasto = ChainedForeignKey(
            SubSubTipoGasto, chained_field='subtipogasto',
            chained_model_field='subtipogasto', null=True, blank=True)
    cuenta = models.CharField(max_length=400, null=False)
    asignado = models.DecimalField(
            max_digits=12, decimal_places=2, blank=True, null=True)
    ejecutado = models.DecimalField(
            max_digits=12, decimal_places=2, blank=False, null=False)

    class Meta:
        unique_together = [['gasto', 'codigo']]
        verbose_name_plural = 'Detalles de gastos'
        verbose_name = 'Detalle de gastos'
        ordering = ['gasto', 'codigo']

    def __unicode__(self):
        return u"{}:{}:{}".format(self.id, self.codigo, self.cuenta)


class TipoProyecto(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    slug = AutoSlugField(populate_from='nombre')

    class Meta:
        verbose_name_plural = 'Tipos de proyectos'
        verbose_name = 'Tipo de proyectos'
        ordering = ['nombre']

    def __unicode__(self):
        return self.nombre


class Inversion(models.Model):
    departamento = models.ForeignKey(Departamento, null=True)
    municipio = models.ForeignKey(Municipio, null=True, blank=True)
    nombremunic = models.CharField(max_length=250, null=True, blank=True)
    fecha = models.DateField(null=False)
    anio = models.IntegerField(null=False, verbose_name=u'Año')
    periodo = models.CharField(max_length=1, null=False)

    class Meta:
        unique_together = [['anio', 'periodo', 'municipio']]
        verbose_name_plural = u'Inversiones'
        verbose_name = u'Inversión'
        ordering = ['anio', 'periodo', 'municipio']

    def __unicode__(self):
        return u"{}:{}:{}".format(self.anio, self.periodo, self.municipio)


class Proyecto(models.Model):
    URBANA = 'U'
    RURAL = 'R'
    OTROS = 'O'
    AREA_CHOICES = (
        (URBANA, 'Urbana'),
        (RURAL, 'Rural'),
        (OTROS, 'Otros'),
    )
    inversion = models.ForeignKey(
        Inversion, related_name='inversion', null=False)
    codigo = models.CharField(max_length=20, null=True)
    nombre = models.CharField(max_length=500)
    tipoproyecto = models.ForeignKey(
        TipoProyecto, related_name='tipo_proyecto', null=True, blank=True)
    catinversion = models.ForeignKey(
        CatInversion, related_name='categoria_inversion',
        null=True, blank=True, verbose_name=u"Categoría de Inversión")
    areageografica = models.CharField(
        choices=AREA_CHOICES, max_length=1, null=True, blank=True)
    asignado = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True)
    ejecutado = models.DecimalField(
        max_digits=12, decimal_places=2, blank=False, null=False)
    ficha = models.FileField(upload_to='proyecto', blank=True, null=True)

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
        unique_together = [['inversion', 'codigo']]
        ordering = ['inversion', 'codigo']

    def __unicode__(self):
        return u"{}:{}:{}".format(self.id, self.codigo, self.nombre)


# financiamiento
class TipoFuenteFmto(models.Model):
    nombre = models.CharField(max_length=250, unique=True)
    slug = AutoSlugField(populate_from='nombre')

    class Meta:
        verbose_name = 'Tipo de Fuente de financiamiento'
        verbose_name_plural = 'Tipos de Fuentes de financiamiento'
        ordering = ['nombre']

    def __unicode__(self):
        return self.nombre


class FuenteFmto(models.Model):
    nombre = models.CharField(max_length=250, unique=True)
    slug = AutoSlugField(populate_from='nombre')
    tipofuente = models.ForeignKey(TipoFuenteFmto)

    class Meta:
        verbose_name = 'Fuente de financiamiento'
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
    municipio = ChainedForeignKey(
            Municipio, chained_field='departamento',
            chained_model_field='depto',
            null=True, blank=True)

    class Meta:
        verbose_name = u'Inversión de fuentes de financiamiento'
        verbose_name_plural = u'Inversiones de fuentes de financiamiento'
        ordering = ['anio', 'periodo', 'municipio']


class InversionFuenteDetalle(models.Model):
    inversionfuente = models.ForeignKey(InversionFuente)
    tipofuente = models.ForeignKey(TipoFuenteFmto)
    fuente = ChainedForeignKey(
            FuenteFmto, chained_field='tipofuente',
            chained_model_field='tipofuente', null=True, blank=True)
    asignado = models.DecimalField(
            max_digits=12, decimal_places=2, blank=True, null=True)
    ejecutado = models.DecimalField(
            max_digits=12, decimal_places=2, blank=False, null=False)

    class Meta:
        verbose_name = u'Detalle de inversión por fuente'
        verbose_name_plural = u'Detalles de inversión por fuente'
        ordering = ['inversionfuente', 'tipofuente', 'fuente']


class Transferencia(models.Model):
    departamento = models.ForeignKey(Departamento, null=True, blank=True)
    municipio = models.ForeignKey(Municipio, null=True, blank=True)
    fecha = models.DateField(null=False)
    anio = models.IntegerField(null=False, verbose_name=u'Año')
    periodo = models.CharField(max_length=1, null=False)
    corriente = models.DecimalField(
            max_digits=12, decimal_places=2, blank=True, null=True)
    capital = models.DecimalField(
            max_digits=12, decimal_places=2, blank=False, null=False)


    class Meta:
        unique_together = [['anio', 'periodo', 'municipio']]
        verbose_name_plural = u'Transferencias'
        verbose_name = u'Transferencia'
        ordering = ['anio', 'periodo', 'municipio']

    def __unicode__(self):
        return u"{}:{}:{}".format(self.anio, self.periodo, self.municipio)
