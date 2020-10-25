from django.db import models
from core.models import Municipio
from sorl.thumbnail import ImageField
from autoslug import AutoSlugField

# Create your models here.
class Banner(models.Model):
    municipio = models.ForeignKey(Municipio, on_delete=models.SET_NULL)
    titulo = models.CharField(max_length=200)
    vertical = models.BooleanField(default=False)
    descripcion = models.CharField(max_length=500, null=True, blank=True)
    enlace = models.CharField(max_length=200, null=True, blank=True)
    orden = models.IntegerField(null=True, blank=True)
    imagen = ImageField(upload_to='banner',null=True,blank=True)
    color = models.CharField(max_length=6)

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
    titulo = models.CharField(max_length=220)
    tipo = models.ForeignKey(TipoDoc,related_name="Tipo", on_delete=models.SET_NULL)
    fecha = models.DateField('fecha',blank=True,null=True)
    descripcion = models.TextField(),
    archivo =  models.FileField(upload_to='documentos', blank=True, null=True)
    imagen = ImageField(upload_to='documento',null=True,blank=True)

    def __unicode__(self):
        return self.titulo

    class Meta:
        ordering = ['titulo']
        verbose_name = 'Documentos'
        verbose_name_plural = 'Documentos'

