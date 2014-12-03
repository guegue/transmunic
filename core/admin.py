from django.contrib import admin
from core.models import * 

# Register your models here.
class GastoFuenteFmtoInline(admin.StackedInline):
    model = GastoFuenteFmto
    extra = 1

class GastoAdmin(admin.ModelAdmin):
    inlines = [GastoFuenteFmtoInline]

class IngresoDetalleInline(admin.TabularInline):
    model = IngresoDetalle
    extra = 1

class IngresoAdmin(admin.ModelAdmin):
    inlines = [IngresoDetalleInline]

class ProyectoDetalleInline(admin.TabularInline):
    model = ProyectoDetalle
    extra = 1

class ProyectoAdmin(admin.ModelAdmin):
    inlines = [ProyectoDetalleInline]

admin.site.register(Ingreso,IngresoAdmin)
admin.site.register(Gasto,GastoAdmin)
admin.site.register(Proyecto,ProyectoAdmin)
