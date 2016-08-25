from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('^IDV/', include('idv.collector.urls', namespace='collector')),
    url('^track/', include('idv.tracker.urls', namespace='tracker'))
]
