from django.views.generic import TemplateView

from .mixins import StaffRequiredMixin


class RequestWrap(StaffRequiredMixin, TemplateView):

    template_name = ''
