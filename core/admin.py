from django.contrib import admin
from core.models import (Profile, Organizacion, Anio, Grafico, CatInversion, TipoGasto,
                         SubTipoGasto, SubSubTipoGasto, OrigenRecurso, OrigenGasto, TipoIngreso,
                         SubSubTipoIngreso, Sub3TipoIngreso, SubTipoIngreso, TipoFuenteFmto, FuenteFmto,
                         InversionFuente, Inversion, Proyecto, Ingreso, Gasto, IngresoRenglon,
                         GastoRenglon, GastoDetalle, IngresoDetalle, InversionFuenteDetalle)

# Register your models here.


class SubSubTipoIngresoInline(admin.TabularInline):
    model = SubSubTipoIngreso
    extra = 5


class SubTipoIngresoAdmin(admin.ModelAdmin):
    inlines = [SubSubTipoIngresoInline]
    list_display = ('nombre', 'tipoingreso', 'slug')
    list_filter = ['tipoingreso']
    search_fields = ('codigo','nombre')


class SubSubTipoIngresoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'subtipoingreso', 'nombre', 'origen')
    list_filter = ['origen', 'subtipoingreso']
    search_fields = ('codigo','nombre','subtipoingreso__codigo')

class Sub3TipoIngresoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'subsubtipoingreso', 'nombre', 'origen')
    list_filter = ['origen', 'subsubtipoingreso']


class GastoDetalleInline(admin.TabularInline):
    model = GastoDetalle
    extra = 1


class GastoAdmin(admin.ModelAdmin):
    list_display = ['id', 'anio','periodo', 'departamento', 'municipio']
    inlines = [GastoDetalleInline]
    list_filter = ('anio', 'periodo','departamento', 'municipio')


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
    list_display = ('municipio', 'departamento', 'fecha')
    inlines = [InversionFuenteDetalleInline]
    list_filter = ('fecha', 'departamento', 'municipio')


class IngresoAdmin(admin.ModelAdmin):
    inlines = [IngresoDetalleInline]
    list_display = ['id', 'anio','periodo', 'departamento', 'municipio']
    list_filter = ('anio', 'departamento', 'municipio')


class TipoIngresoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'clasificacion')
    list_filter = ['clasificacion']


class ProyectoInline(admin.TabularInline):
    model = Proyecto
    extra = 1

    class Meta:
        localized_fields = ('__all__')


class InversionAdmin(admin.ModelAdmin):
    inlines = [ProyectoInline]
    list_display = ['id', 'departamento', 'municipio', 'fecha', 'periodo']
    list_filter = ('departamento', 'municipio', 'periodo', 'anio')


admin.site.register(Profile)
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
admin.site.register(Sub3TipoIngreso, Sub3TipoIngresoAdmin)
admin.site.register(SubTipoIngreso, SubTipoIngresoAdmin)
admin.site.register(TipoFuenteFmto)
admin.site.register(FuenteFmto)
admin.site.register(InversionFuente,InversionFuenteAdmin)
admin.site.register(Inversion,InversionAdmin)
admin.site.register(Proyecto)
admin.site.register(Ingreso,IngresoAdmin)
admin.site.register(Gasto,GastoAdmin)
admin.site.register(IngresoRenglon)
admin.site.register(GastoRenglon)
