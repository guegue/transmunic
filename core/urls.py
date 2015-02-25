from django.conf.urls import patterns, include, url
from . import charts

urlpatterns = patterns('',
    url(r'^oim$', 'core.charts.oim_pie_chart', name='oim'),
    url(r'^ogm$', 'core.charts.ogm_pie_chart', name='ogm'),
    url(r'^inversion$', 'core.charts.inversion_pie_chart', name='inversion'),
    url(r'^gf$', 'core.charts.gf_chart', name='gf'),
)
