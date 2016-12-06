from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'success$', views.RequestWrapSuccess.as_view(),
        name='request-wrap-success'),
    url(r'^$', views.RequestWrap.as_view(), name='request-wrap'),
    url(r'^epack-login/$', views.EpackLogin.as_view(), name='epack-login'),
    url(r'^epack-search/$', views.EpackSearch.as_view(), name='epack-search'),
    url(r'^lwi-login/$', views.LwiStaffLogin.as_view(), name='lwi-login'),
    url(r'^lwi-requests/$', views.LwiRequests.as_view(), name='lwi-requests'),
    url(r'^lwi-request-details/$', views.LwiRequestDetails.as_view(),
        name='lwi-request-details'),
]
