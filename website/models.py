from django.db import models
from core.models import Municipio
from sorl.thumbnail import ImageField

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

