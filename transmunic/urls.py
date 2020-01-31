from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin

from website.views import DocumentoTipoListView
from core.views import home, municipio

admin.autodiscover()

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^core/', include('core.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^chaining/', include('pixelfields_smart_selects.urls')),
    url(r'^resumen-municipal', municipio, name='budget-summary'),
    url(r'^resumen-municipal/(?P<year>[0-9]{4})/$', municipio, name='anual-budget-summary'),
    url(r'^documento/(?P<slug>[-\w]+)/$',
        DocumentoTipoListView.as_view(), name='documento_by_tipo'),
    url(r'^explorer/', include('explorer.urls')),
    url(r'^municipio/(?P<slug>[-\w]+)/$', municipio, name='municipio'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
