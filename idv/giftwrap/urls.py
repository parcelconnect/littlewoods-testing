from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.RequestWrap.as_view(), name='request-wrap'),
]
