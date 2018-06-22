from django.urls import path

from . import views

app_name = 'collector'
urlpatterns = [
    path('', views.collect, name='collect'),
    path('sign-s3-request/', views.sign_s3_request, name='sign-s3-request'),
]
