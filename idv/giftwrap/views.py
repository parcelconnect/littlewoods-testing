from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from .forms import GiftWrapRequestForm
from .models import GiftWrapRequest, GiftWrapRequestStatus


class RequestWrap(CreateView):
    template_name = 'giftwrap/customer_request.html'
    success_url = 'success'
    form_class = GiftWrapRequestForm


class RequestWrapSuccess(TemplateView):
    template_name = 'giftwrap/success.html'


class EpackLogin(TemplateView):
    template_name = 'giftwrap/epack_login.html'

    def post(self, request):
        username = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(request.GET.get('next'))
        else:
            return super().render_to_response({})


epack_login_required = login_required(
    login_url=reverse_lazy("giftwrap:epack-login")
)


@method_decorator(epack_login_required, name="dispatch")
class EpackSearch(TemplateView):
    template_name = 'giftwrap/epack_search.html'

    def get_context_data(self):
        context = super().get_context_data()
        upi = self.request.GET.get('upi')
        if upi:
            context['upi'] = upi
            details = self._get_orders_for_upi(upi)
            context['order_details'] = details

        return context

    def _get_orders_for_upi(self, upi):
        return GiftWrapRequest.objects.filter(
            upi=upi,
            status=GiftWrapRequestStatus.Success.value,
        ).values(
            'divert_contact_name',
            'divert_address',
            'card_message'
        )
