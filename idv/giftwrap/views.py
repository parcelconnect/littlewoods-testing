from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from .forms import GiftWrapRequestForm


class RequestWrap(CreateView):
    template_name = 'giftwrap/request_wrap.html'
    success_url = 'success'
    form_class = GiftWrapRequestForm


class RequestWrapSuccess(TemplateView):
    template_name = 'giftwrap/success.html'
