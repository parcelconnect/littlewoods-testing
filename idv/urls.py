from django.contrib import admin
from django.urls import include, path, re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('IDV/', include('idv.collector.urls', namespace='collector')),
    re_path(r'(?P<verification_type>\w+)-IDV/',
            include('idv.collector.urls', namespace='parametrized-collector')),
    path('track/', include('idv.tracker.urls', namespace='tracker')),
    path('gift-wrapping/', include('idv.giftwrap.urls', namespace='giftwrap')),
]
