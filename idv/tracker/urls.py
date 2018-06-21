from django.conf.urls import url

from . import views

app_name = 'tracker'
urlpatterns = [
    url(r'^$', views.track, name='track'),
    url(r'^events/?$', views.get_tracking_events, name='get-events'),
]
