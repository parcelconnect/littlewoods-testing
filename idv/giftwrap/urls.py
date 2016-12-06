from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'success$', views.RequestWrapSuccess.as_view(),
        name='request-wrap-success'),
    url(r'^$', views.RequestWrap.as_view(), name='request-wrap'),
    url(r'^epack-login/', views.EpackLogin.as_view(), name='epack-login'),
    url(r'^order-search/', views.EpackSearch.as_view(), name='epack-search'),
]
