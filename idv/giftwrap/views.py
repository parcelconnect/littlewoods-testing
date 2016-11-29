from django.views.generic import FormView

from .forms import GiftWrapRequestForm


class RequestWrap(FormView):
    template_name = 'giftwrap/request_wrap.html'
    form_class = GiftWrapRequestForm
