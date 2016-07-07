import json

from idv.common.http import extract_json_from_GET

from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render

from . import domain
from .forms import AccountForm


def collect(request):
    context = {}
    context['json_context'] = json.dumps({
        'sign_s3_request_url': reverse('collector:sign-s3-request')
    })
    return render(request, 'collector/collect.html', context=context)


@transaction.atomic
def sign_s3_request(request):
    file_data = extract_json_from_GET(request, 'file_data')

    account_form = AccountForm(request.GET)
    if not account_form.is_valid():
        return JsonResponse({'errors': account_form.errors}, status=400)

    account = domain.get_or_create_account(
        account_form.cleaned_data['email'],
        account_form.cleaned_data['account_number']
    )
    data = {}
    for filename, filetype in file_data.items():
        credential = domain.create_credential(account, filename)
        signed_url = domain.generate_presigned_s3_url(
            credential.s3_key, filetype)
        data[filename] = signed_url
    return JsonResponse(data)
