from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.Collect.as_view(), name='collect'),
    url(r'^sign-s3-request/$', views.sign_s3_request, name='sign-s3-request'),
]
