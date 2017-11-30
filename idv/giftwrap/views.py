from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from . import domain
from .forms import GiftWrapRequestForm, UPIForm
from .mixins import SpecialDateMixin
from .models import GiftWrapRequest
from .types import GiftWrapRequestStatus

##########################################################
#                     Generic views                      #
##########################################################


class TemplateLoginView(TemplateView):

    def post(self, request):
        username = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(request.GET.get('next'))
        else:
            return super().render_to_response({})


##########################################################
#                       LWI views                        #
##########################################################

lwi_login_required = login_required(
    login_url=reverse_lazy("giftwrap:lwi-login")
)


class LWILogin(SpecialDateMixin, TemplateLoginView):
    template_name = 'giftwrap/lwi_login.html'


@method_decorator(lwi_login_required, name="dispatch")
class RequestList(SpecialDateMixin, TemplateView):
    template_name = 'giftwrap/lwi_requests.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['pending_requests'] = GiftWrapRequest.objects.new()
        context['error_requests'] = GiftWrapRequest.objects.error()
        return context


@method_decorator(lwi_login_required, name="dispatch")
class RequestDetails(SpecialDateMixin, TemplateView):
    template_name = 'giftwrap/lwi_request_details.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        pk = kwargs['pk']
        context['gw_request'] = self._get_gw_request(pk)
        context['result'] = None
        return context

    def _get_gw_request(self, pk):
        return GiftWrapRequest.objects.get(pk=pk)

    def post(self, request, pk):
        context = self.get_context_data(pk=pk)
        gw_request = context['gw_request']
        form = UPIForm(request.POST)
        if form.is_valid():
            domain.update_upi(gw_request, form.cleaned_data['upi'])
            result = domain.request_gift_wrap(gw_request)
            context['result'] = result
            if result == GiftWrapRequestStatus.Success.value:
                msg = ('Success requesting gift wrapping for UPI {}'
                       .format(form.cleaned_data['upi']))
                messages.success(request, msg)
                url = reverse_lazy('giftwrap:lwi-requests')
                return redirect(url)
            else:
                status = 202
        else:
            status = 400
            context['result'] = "validation-error"
            context['form'] = form
        return super().render_to_response(context, status=status)

    def delete(self, request, pk):
        context = self.get_context_data(pk=pk)
        context['gw_request'].mark_as_rejected()
        messages.success(request, 'Request Rejected')
        return HttpResponse(status=200)


##########################################################
#                       Epack views                      #
##########################################################

epack_login_required = login_required(
    login_url=reverse_lazy("giftwrap:epack-login")
)


class EpackLogin(SpecialDateMixin, TemplateLoginView):
    template_name = 'giftwrap/epack_login.html'


@method_decorator(epack_login_required, name="dispatch")
class EpackSearch(SpecialDateMixin, TemplateView):
    template_name = 'giftwrap/epack_search.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.request.GET.get('upi'):
            form = UPIForm(self.request.GET)
            if form.is_valid():
                details = domain.get_orders_for_upi(form.cleaned_data['upi'])
                if details:
                    context['order_details'] = details
                else:
                    form.add_error("upi", "UPI not found.")
            context['form'] = form

        return context


##########################################################
#                    Customer views                      #
##########################################################

class RequestWrap(SpecialDateMixin, CreateView):
    template_name = 'giftwrap/customer_request.html'
    success_url = 'success'
    form_class = GiftWrapRequestForm


class RequestWrapSuccess(SpecialDateMixin, TemplateView):
    template_name = 'giftwrap/success.html'
