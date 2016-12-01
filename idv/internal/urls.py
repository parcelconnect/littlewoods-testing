from django.conf.urls import url

from . import views


urlpatterns = [
    url(
        r'^gift-wrap/?',
        views.RequestWrap.as_view(),
        name='request-gift-wrap'
    ),
]
