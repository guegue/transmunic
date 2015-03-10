from django.contrib import admin
from lugar.models import * 

# Register your models here.
class PoblacionInline(admin.TabularInline):
    model = Poblacion
    extra = 5

class MunicipioAdmin(admin.ModelAdmin):
    list_display = ['id','depto','nombre']
    inlines = [PoblacionInline]
    list_filter = ['depto']

admin.site.register(Departamento)
admin.site.register(Municipio,MunicipioAdmin)
admin.site.register(Comarca)
admin.site.register(ClasificacionMunic)
