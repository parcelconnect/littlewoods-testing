from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'success$', views.RequestWrapSuccess.as_view(),
        name='request-wrap-success'),
    url(r'^$', views.RequestWrap.as_view(), name='request-wrap'),
]
