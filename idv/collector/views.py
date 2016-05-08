import json

from idv.common import aws
from idv.common.http import extract_json_from_GET

from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View

from . import domain


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


@transaction.atomic
def sign_s3_request(request):
    email = request.GET['email']
    account_number = request.GET['account']
    file_data = extract_json_from_GET(request, 'fileData')

    account = domain.get_or_create_account(email, account_number)

    data = {}
    for filename, filetype in file_data.items():
        credential = domain.create_credential(account, filename)
        signed_url = aws.generate_presigned_s3_url(
            'put_object', credential.s3_key, ContentType=filetype)
        data[filename] = signed_url
    return JsonResponse(data)
