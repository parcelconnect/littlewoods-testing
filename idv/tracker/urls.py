from django.urls import path

from . import views

app_name = 'tracker'
urlpatterns = [
    path('', views.track, name='track'),
    path('events/?', views.get_tracking_events, name='get-events'),
]
