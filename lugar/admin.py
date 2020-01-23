from django.contrib import admin
from lugar.models import * 

# Register your models here.
class ClasificacionMunicInline(admin.TabularInline):
    model = ClasificacionMunicAno
    extra = 1

class PoblacionInline(admin.TabularInline):
    model = Poblacion
    extra = 1

class MunicipioAdmin(admin.ModelAdmin):
    list_display = ['id','depto','nombre']
    inlines = [PoblacionInline,ClasificacionMunicInline]
    list_filter = ['depto']

admin.site.register(Departamento)
admin.site.register(Municipio,MunicipioAdmin)
admin.site.register(Comarca)
admin.site.register(ClasificacionMunic)
admin.site.register(Periodo)
admin.site.register(PeriodoMunic)
