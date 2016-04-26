import json

from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.views.generic import View


class Collect(View):

    def get(self, request):
        context = {}
        context['json_context'] = json.dumps({
            'sign_s3_request_url': reverse('collector:sign-s3-request')
        })
        return render(request, 'collector/collect.html', context=context)

    def post(self, request):
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(reverse('collector:collect'))
