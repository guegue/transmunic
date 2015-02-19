from django.contrib import admin
from lugar.models import * 

# Register your models here.
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ['id','depto','nombre']

admin.site.register(Departamento)
admin.site.register(Municipio,MunicipioAdmin)
admin.site.register(Comarca)
