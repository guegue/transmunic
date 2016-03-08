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
    list_display = ('codigo','subtipoingreso','nombre','origen')
    list_filter = ['origen','subtipoingreso']

class GastoDetalleInline(admin.TabularInline):
    model = GastoDetalle
    extra = 1

class GastoAdmin(admin.ModelAdmin):
    list_display = ('municipio','departamento','fecha')
    inlines = [GastoDetalleInline]
    list_filter = ('fecha','departamento','municipio')

class IngresoDetalleInline(admin.TabularInline):
    model = IngresoDetalle
    extra = 1
    class Meta:
        localized_fields = ('__all__')

class InversionFuenteDetalleInline(admin.TabularInline):
    model = InversionFuenteDetalle
    extra = 1
    class Meta:
        localized_fields = ('__all__')

class InversionFuenteAdmin(admin.ModelAdmin):
    list_display = ('municipio','departamento','fecha')
    inlines = [InversionFuenteDetalleInline]
    list_filter = ('fecha','departamento','municipio')


class IngresoAdmin(admin.ModelAdmin):
    inlines = [IngresoDetalleInline]
    list_display = ['id','fecha', 'departamento','municipio']
    list_filter = ('fecha','departamento','municipio')

class TipoIngresoAdmin(admin.ModelAdmin):
    list_display = ('codigo','nombre','clasificacion')
    list_filter = ['clasificacion']

class ProyectoInline(admin.TabularInline):
    model = Proyecto
    extra = 1
    class Meta:
        localized_fields = ('__all__')

class InversionAdmin(admin.ModelAdmin):
    inlines = [ProyectoInline]
    list_display = ['id','departamento','municipio', 'fecha','periodo']
    list_filter = ('departamento','municipio', 'periodo', 'anio')

admin.site.register(Organizacion)
admin.site.register(Anio)
admin.site.register(Grafico)
admin.site.register(CatInversion)
admin.site.register(TipoGasto)
admin.site.register(SubTipoGasto)
admin.site.register(SubSubTipoGasto)
admin.site.register(OrigenRecurso)
admin.site.register(OrigenGasto)
admin.site.register(TipoIngreso,TipoIngresoAdmin)
admin.site.register(SubSubTipoIngreso, SubSubTipoIngresoAdmin)
admin.site.register(SubTipoIngreso, SubTipoIngresoAdmin)
admin.site.register(TipoFuenteFmto)
admin.site.register(FuenteFmto)
admin.site.register(InversionFuente,InversionFuenteAdmin)
admin.site.register(Inversion,InversionAdmin)
admin.site.register(Proyecto)
admin.site.register(Ingreso,IngresoAdmin)
admin.site.register(Gasto,GastoAdmin)
