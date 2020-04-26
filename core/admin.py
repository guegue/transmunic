from django.contrib import admin
from core.models import (Profile, Organizacion, Anio,
                         AnioTransferencia, Grafico,
                         CatInversion, TipoGasto,
                         SubTipoGasto, SubSubTipoGasto,
                         OrigenRecurso, OrigenGasto,
                         OrigenGastoPersonal, TipoIngreso,
                         SubSubTipoIngreso, Sub3TipoIngreso,
                         SubTipoIngreso, TipoFuenteFmto,
                         FuenteFmto, InversionFuente,
                         Transferencia, Inversion,
                         Proyecto, Ingreso, Gasto,
                         IngresoRenglon, GastoRenglon,
                         GastoDetalle, IngresoDetalle,
                         InversionFuenteDetalle,
                         OrigenIngresosCorrientes,
                         OrigenGastosCorrientes)


# Register your models here.

# Change default query


class AdminForUserMixin:

    def get_queryset(self, request):
        if request.user:
            return self.model.objects.for_user(request.user)
        return super().get_queryset(request)


class SubSubTipoIngresoInline(admin.TabularInline):
    model = SubSubTipoIngreso
    extra = 5


class SubTipoIngresoAdmin(admin.ModelAdmin):
    inlines = [SubSubTipoIngresoInline]
    list_display = ('codigo', 'nombre', 'tipoingreso',
                    'slug', 'origen_ic')
    list_display_links = ('codigo', 'nombre')
    list_filter = ['tipoingreso', 'origen_ic']
    search_fields = ('codigo', 'nombre')


class SubSubTipoIngresoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'subtipoingreso', 'nombre', 'origen')
    list_filter = ['origen', 'subtipoingreso']
    search_fields = ('codigo', 'nombre', 'subtipoingreso__codigo')


class Sub3TipoIngresoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'subsubtipoingreso', 'nombre', 'origen')
    list_filter = ['origen', 'subsubtipoingreso']


class GastoDetalleInline(admin.TabularInline):
    model = GastoDetalle
    extra = 1


class GastoAdmin(AdminForUserMixin, admin.ModelAdmin):
    list_display = ['id', 'anio', 'periodo', 'departamento', 'municipio']
    inlines = [GastoDetalleInline]
    list_filter = ('anio', 'periodo', 'departamento', 'municipio')


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


class IngresoAdmin(AdminForUserMixin, admin.ModelAdmin):
    inlines = [IngresoDetalleInline]
    list_display = ['id', 'anio', 'periodo', 'departamento', 'municipio']
    list_filter = ('anio', 'departamento', 'municipio')


class TipoIngresoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre',
                    'clasificacion', 'nuevo_catalogo', ]
    list_display_links = ['codigo', 'nombre']
    list_filter = ['clasificacion']
    search_fields = ['codigo', 'nombre']


class ProyectoInline(admin.TabularInline):
    model = Proyecto
    extra = 1

    class Meta:
        localized_fields = ('__all__')


class InversionAdmin(AdminForUserMixin, admin.ModelAdmin):
    inlines = [ProyectoInline]
    list_display = ['id', 'departamento', 'municipio', 'fecha', 'periodo']
    list_filter = ('departamento', 'municipio', 'periodo', 'anio')


class SubSubTipoGastoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'clasificacion']
    list_filter = ('origen', 'clasificacion', 'subtipogasto__codigo')


class TransferenciaAdmin(admin.ModelAdmin):
    list_display = ['id', 'anio', 'periodo', 'departamento', 'municipio']
    list_filter = ('anio', 'departamento', 'municipio')


class SubTipoGastoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'shortname', 'tipogasto', 'origen_gp']
    list_display_links = ['codigo', 'nombre']
    list_filter = ('tipogasto', 'origen_gp')
    search_fields = ['nombre', 'codigo']


class OrigendeCorrientesAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'shortname', 'orden']
    list_display_links = ['id', 'nombre']
    search_fields = ['nombre', 'codigo']


admin.site.register(Profile)
admin.site.register(Organizacion)
admin.site.register(Anio)
admin.site.register(AnioTransferencia)
admin.site.register(Grafico)
admin.site.register(CatInversion)
admin.site.register(OrigenIngresosCorrientes, OrigendeCorrientesAdmin)
admin.site.register(OrigenGastosCorrientes, OrigendeCorrientesAdmin)
admin.site.register(TipoGasto)
admin.site.register(SubTipoGasto, SubTipoGastoAdmin)
admin.site.register(SubSubTipoGasto, SubSubTipoGastoAdmin)
admin.site.register(OrigenRecurso)
admin.site.register(OrigenGasto)
admin.site.register(OrigenGastoPersonal)
admin.site.register(TipoIngreso, TipoIngresoAdmin)
admin.site.register(SubSubTipoIngreso, SubSubTipoIngresoAdmin)
admin.site.register(Sub3TipoIngreso, Sub3TipoIngresoAdmin)
admin.site.register(SubTipoIngreso, SubTipoIngresoAdmin)
admin.site.register(TipoFuenteFmto)
admin.site.register(FuenteFmto)
admin.site.register(InversionFuente, InversionFuenteAdmin)
admin.site.register(Inversion, InversionAdmin)
admin.site.register(Proyecto)
admin.site.register(Ingreso, IngresoAdmin)
admin.site.register(Gasto, GastoAdmin)
admin.site.register(IngresoRenglon)
admin.site.register(GastoRenglon)
admin.site.register(Transferencia, TransferenciaAdmin)
