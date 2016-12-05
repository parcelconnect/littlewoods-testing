from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from .forms import GiftWrapRequestForm, EpackLoginForm, EpackSearchForm


class RequestWrap(CreateView):
    template_name = 'giftwrap/customer_request.html'
    success_url = 'success'
    form_class = GiftWrapRequestForm


class RequestWrapSuccess(TemplateView):
    template_name = 'giftwrap/success.html'


class EpackLogin(CreateView):
    template_name = 'giftwrap/epack_login.html'
    success_url = 'success'
    form_class = EpackLoginForm


class EpackSearch(CreateView):
    template_name = 'giftwrap/order_search.html'
    success_url = 'success'
    form_class = EpackSearchForm


class EpackSuccess(TemplateView):
    template_name = 'giftwrap/success.html'
