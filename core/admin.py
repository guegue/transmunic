from django.contrib import admin
from core.models import *

# Register your models here.
class SubSubTipoIngresoInline(admin.TabularInline):
    model = SubSubTipoIngreso
    extra = 5
class SubTipoIngresoAdmin(admin.ModelAdmin):
    inlines = [SubSubTipoIngresoInline]

class GastoFuenteFmtoInline(admin.StackedInline):
    model = GastoFuenteFmto
    extra = 1

class GastoDetalleInline(admin.TabularInline):
    model = GastoDetalle
    extra = 1

class GastoAdmin(admin.ModelAdmin):
    inlines = [GastoFuenteFmtoInline,GastoDetalleInline]

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

admin.site.register(CatInversion)
admin.site.register(TipoGasto)
admin.site.register(SubTipoGasto)
admin.site.register(OrigenRecurso)
admin.site.register(TipoIngreso)
admin.site.register(SubTipoIngreso, SubTipoIngresoAdmin)
admin.site.register(FuenteFmto)
admin.site.register(Donante)
admin.site.register(Ingreso,IngresoAdmin)
admin.site.register(Gasto,GastoAdmin)
admin.site.register(Proyecto,ProyectoAdmin)
admin.site.register(AreaGeografica)
