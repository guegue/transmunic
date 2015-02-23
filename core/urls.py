from django.conf.urls import patterns, include, url
from . import charts

urlpatterns = patterns('',
    url(r'^oim$', 'core.charts.oim_pie_chart', name='home'),
)
