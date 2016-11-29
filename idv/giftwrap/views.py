from django.views.generic import TemplateView


class RequestWrap(TemplateView):

    template_name = 'giftwrap/request_wrap.html'
