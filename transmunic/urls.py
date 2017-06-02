from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from website.views import (DocumentoTipoListView)
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'core.views.home', name='home'),
    url(r'^core/', include('core.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^chaining/', include('pixelfields_smart_selects.urls')),
    url(r'^(?P<slug>[-\w]+)/$', 'core.views.municipio', name='municipio'),
    url(r'^documento/(?P<slug>[-\w]+)/$', DocumentoTipoListView.as_view(), name='documento_by_tipo'),
)




from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()

urlpatterns += patterns('',
(r'^media/(?P<path>.*)$', 'django.views.static.serve',
{'document_root': settings.MEDIA_ROOT}),

                            )

urlpatterns += patterns('',
(r'^static/(?P<path>.*)$', 'django.views.static.serve',
{'document_root': settings.STATIC_ROOT}),

)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
