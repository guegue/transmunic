from django.contrib import admin
from core.models import *

# Register your models here.
class SubSubTipoIngresoInline(admin.TabularInline):
    model = SubSubTipoIngreso
    extra = 5

class SubTipoIngresoAdmin(admin.ModelAdmin):
    inlines = [SubSubTipoIngresoInline]
    list_display = ('nombre','tipoingreso','slug')
    list_filter = ['tipoingreso']

class SubSubTipoIngresoAdmin(admin.ModelAdmin):
    list_display = ('id','subtipoingreso','nombre')
    list_filter = ['subtipoingreso']

class GastoDetalleInline(admin.TabularInline):
    model = GastoDetalle
    extra = 1

class GastoAdmin(admin.ModelAdmin):
    inlines = [GastoDetalleInline]

class IngresoDetalleInline(admin.TabularInline):
    model = IngresoDetalle
    extra = 1
    class Meta:
        localized_fields = ('__all__')


class IngresoAdmin(admin.ModelAdmin):
    inlines = [IngresoDetalleInline]
    list_display = ['id','fecha', 'departamento','municipio']
    list_filter = ('fecha','departamento','municipio')

class ProyectoDetalleInline(admin.TabularInline):
    model = ProyectoDetalle
    extra = 1

class ProyectoAdmin(admin.ModelAdmin):
    inlines = [ProyectoDetalleInline]

admin.site.register(CatInversion)
admin.site.register(TipoGasto)
admin.site.register(SubTipoGasto)
admin.site.register(SubSubTipoGasto)
admin.site.register(OrigenRecurso)
admin.site.register(TipoIngreso)
admin.site.register(SubSubTipoIngreso, SubSubTipoIngresoAdmin)
admin.site.register(SubTipoIngreso, SubTipoIngresoAdmin)
admin.site.register(FuenteFmto)
admin.site.register(Donante)
#admin.site.register(Ingreso)
admin.site.register(Ingreso,IngresoAdmin)
admin.site.register(Gasto,GastoAdmin)
admin.site.register(Proyecto,ProyectoAdmin)
admin.site.register(AreaGeografica)
