from django.conf.urls import include, url
from django.views.generic import TemplateView, ListView
from model_report import report
from . import charts
from core import views
from core.importer import UploadExcelView, ResultadoDetailView
from core.charts import funcionamiento, personal, ago, aci, misc, ep
from core.models import Organizacion

report.autodiscover()

urlpatterns = [
    url(r'^importar/$', UploadExcelView.as_view()),
    url(r'^resultado/(?P<table>ingreso|gasto)/(?P<pk>\d+)/$', ResultadoDetailView.as_view(),
        name='ingreso-detail'),
    url(r'^lista$', TemplateView.as_view(template_name='lista.html')),
    url(r'^organizaciones$', ListView.as_view(model=Organizacion)),
    url(r'^gasto-minimo-sector$', views.inversion_minima_sector_view, name='gasto_minimo_sector'),
    url(r'^oim$', views.oim_view, name='origen_ingresos'),
    url(r'^ogm$', views.ogm_view, name='origen_gastos'),
    url(r'^inversion-categoria$', views.inversion_categoria_view, name='inversion_categoria'),
    url(r'^gf$', charts.funcionamiento.gf_chart, name='gastos_funcion'),
    url(r'^gpersonal$', charts.personal.gpersonal_chart, name='gastos_personal'),
    url(r'^ago$', charts.ago.ago_chart, name='autonomia_gastos'),
    url(r'^aci$', charts.aci.aci_chart, name='ahorro_corriente'),
    url(r'^psd$', charts.misc.psd_chart, name='peso_deuda'),
    url(r'^ep$', charts.ep.ep_chart, name='ejecucion_presupuesto'),
    url(r'^inversion-area$', views.inversion_area_view, name='inversion_area'),
    url(r'^inversion$', views.inversion_view, name='inversion'),
    url(r'^fuentes$', views.fuentes_view, name='fuentes'),
    url(r'^detalle-presupuesto$', views.descargar_detalle, name='detalle_presupuesto'),
    url(r'', include('model_report.urls')),
]
