from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from . import charts

urlpatterns = patterns('',
    url(r'^lista$', TemplateView.as_view(template_name='lista.html')),
    url(r'^gasto-minimo-sector$', 'core.charts.inversion_minima_sector_chart', name='gasto_minimo_sector'),
    url(r'^oim$', 'core.views.oim_view', name='origen_ingresos'),
    url(r'^ogm$', 'core.views.ogm_view', name='origen_gastos'),
    url(r'^inversion-categoria$', 'core.charts.inversion_categoria_chart', name='inversion_categoria'),
    url(r'^gf$', 'core.charts.gf_chart', name='gastos_funcion'),
    url(r'^gpersonal$', 'core.charts.gpersonal_chart', name='gastos_personal'),
    url(r'^ago$', 'core.charts.ago_chart', name='autonomia_gastos'),
    url(r'^aci$', 'core.charts.aci_chart', name='ahorro_corriente'),
    url(r'^psd$', 'core.charts.psd_chart', name='peso_deuda'),
    url(r'^ep$', 'core.charts.ep_chart', name='ejecucion_presupuesto'),
    url(r'^inversion-area$', 'core.views.inversion_area_view', name='inversion_area'),
    url(r'^inversion$', 'core.views.inversion_view', name='inversion'),
    url(r'^fuentes$', 'core.views.fuentes_view', name='fuentes'),
)
