from django.conf.urls import url

from . import views

app_name = 'collector'
urlpatterns = [
    url(r'^$', views.collect, name='collect'),
    url(r'^sign-s3-request/$', views.sign_s3_request, name='sign-s3-request'),
]
