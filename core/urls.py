from django.conf.urls import patterns, include, url
from . import charts

urlpatterns = patterns('',
    url(r'^oim$', 'core.charts.oim_pie_chart', name='origen_ingresos'),
    url(r'^ogm$', 'core.charts.ogm_pie_chart', name='origen_gastos'),
    url(r'^inversion$', 'core.charts.inversion_pie_chart', name='inversion'),
    url(r'^gf$', 'core.charts.gf_chart', name='gastos_funcion'),
    url(r'^gpersonal$', 'core.charts.gpersonal_chart', name='gastos_personal'),
    url(r'^ago$', 'core.charts.ago_chart', name='autonomia_gastos'),
    url(r'^aci$', 'core.charts.aci_chart', name='ahorro_corriente'),
    url(r'^psd$', 'core.charts.psd_chart', name='peso_deuda'),
)
