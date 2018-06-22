from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),

    path('IDV/', include('idv.collector.urls', namespace='collector')),
    path('track/', include('idv.tracker.urls', namespace='tracker')),
    path('gift-wrapping/', include('idv.giftwrap.urls', namespace='giftwrap')),
]
