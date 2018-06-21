from django.conf.urls import url

from . import views

app_name = 'giftwrap'
urlpatterns = [
    url(r'success$', views.RequestWrapSuccess.as_view(),
        name='request-wrap-success'),
    url(r'^$', views.RequestWrap.as_view(), name='request-wrap'),
    url(r'^epack-login/$', views.EpackLogin.as_view(), name='epack-login'),
    url(r'^epack-search/$', views.EpackSearch.as_view(), name='epack-search'),
    url(r'^internal-login/$', views.LWILogin.as_view(), name='lwi-login'),
    url(r'^requests/$', views.RequestList.as_view(), name='lwi-requests'),
    url(r'^requests/(?P<pk>\d+)$', views.RequestDetails.as_view(),
        name='lwi-request-details'),
]
