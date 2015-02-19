from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'core.views.home', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^chaining/', include('pixelfields_smart_selects.urls')),
)
