from django.urls import path

from . import views

app_name = 'giftwrap'
urlpatterns = [
    path('success', views.RequestWrapSuccess.as_view(),
         name='request-wrap-success'),
    path('', views.RequestWrap.as_view(), name='request-wrap'),
    path('epack-login/', views.EpackLogin.as_view(), name='epack-login'),
    path('epack-search/', views.EpackSearch.as_view(), name='epack-search'),
    path('internal-login/', views.LWILogin.as_view(), name='lwi-login'),
    path('requests/', views.RequestList.as_view(), name='lwi-requests'),
    path('requests/<int:pk>/', views.RequestDetails.as_view(),
         name='lwi-request-details'),
]
