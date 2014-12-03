# -*- coding: utf-8 -*- 
from django.contrib import admin
from website.models import * 

class SubSubTipoIngresoInline(admin.TabularInline):
    model = SubSubTipoIngreso
    extra = 5
class SubTipoIngresoAdmin(admin.ModelAdmin):
    inlines = [SubSubTipoIngresoInline]

admin.site.register(Departamento)
admin.site.register(Municipio)
admin.site.register(Comarca)
admin.site.register(CatInversion)
admin.site.register(TipoGasto)
admin.site.register(SubTipoGasto)
admin.site.register(OrigenRecurso)
admin.site.register(TipoIngreso)
admin.site.register(SubTipoIngreso, SubTipoIngresoAdmin)
admin.site.register(FuenteFmto)
admin.site.register(AreaGeografica)
admin.site.register(Banner)
admin.site.register(Donante)
admin.site.register(TipoProyecto)

