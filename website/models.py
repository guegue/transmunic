from django.db import models
from core.models import Municipio
from sorl.thumbnail import ImageField
from autoslug import AutoSlugField

# Create your models here.
class Banner(models.Model):
    municipio = models.ForeignKey(Municipio)
    titulo = models.CharField(max_length=200)
    vertical = models.BooleanField(default=False)
    descripcion = models.CharField(max_length=500, null=True, blank=True)
    enlace = models.CharField(max_length=200, null=True, blank=True)
    orden = models.IntegerField(null=True, blank=True)
    imagen = ImageField(upload_to='banner',null=True,blank=True)

    class Meta:
        ordering = ['orden']
    def __unicode__(self):
        return self.titulo

class TipoDoc(models.Model):
    titulo = models.CharField(max_length=120)
    slug = AutoSlugField(populate_from='titulo')

    def __unicode__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Tipo'

class Documento(models.Model):
    titulo = models.CharField(max_length=120)
    tipo = models.ForeignKey(TipoDoc,related_name="Tipo")
    fecha = models.DateField('fecha',blank=True,null=True)
    descripcion = models.TextField(),
    archivo =  models.FileField(upload_to='documentos', blank=True, null=True)

    def __unicode__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Documentos'
        verbose_name_plural = 'Documentos'

