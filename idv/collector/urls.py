from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.Collect.as_view(), name='collect')
]
