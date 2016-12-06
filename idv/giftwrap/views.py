from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from .forms import GiftWrapRequestForm
from .models import GiftWrapRequest


class RequestWrap(CreateView):
    template_name = 'giftwrap/customer_request.html'
    success_url = 'success'
    form_class = GiftWrapRequestForm


class RequestWrapSuccess(TemplateView):
    template_name = 'giftwrap/success.html'


class EpackLogin(TemplateView):
    template_name = 'giftwrap/epack_login.html'
    success_url = 'success'


class EpackSearch(TemplateView):
    template_name = 'giftwrap/order_search.html'

    def get_context_data(self):
        context = super().get_context_data()
        upi = self.request.GET.get('upi')
        if upi:
            context['upi'] = upi
            details = self._get_orders_for_upi(upi)
            context['order_details'] = details

        return context

    def _get_orders_for_upi(self, upi):
        return GiftWrapRequest.objects.filter(upi=upi).values(
            'divert_contact_name',
            'divert_address',
            'card_message'
        )
