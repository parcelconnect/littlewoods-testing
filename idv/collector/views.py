from django.views.generic import TemplateView


class Collect(TemplateView):

    template_name = 'collector/collect.html'
