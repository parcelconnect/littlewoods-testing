import json
from collections import OrderedDict

from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from idv.collector.settings.django import VERIFICATION_TYPES

from . import domain
from .forms import AccountForm


def collect(request, verification_type='normal'):
    if verification_type not in VERIFICATION_TYPES:
        raise Http404("Page not found")

    context = {'json_context': json.dumps({
        'sign_s3_request_url':
            reverse('parametrized-collector:sign-s3-request',
                    kwargs={'verification_type': verification_type})
    })}
    return render(request, 'collector/collect.html', context=context)


@transaction.atomic
@require_http_methods(["POST"])
def sign_s3_request(request, verification_type='normal'):
    if verification_type not in VERIFICATION_TYPES:
        raise Http404("Page not found")

    files_info = json.loads(request.POST.get("files_info"),
                            object_pairs_hook=OrderedDict)
    account_form = AccountForm(request.POST)
    if not account_form.is_valid():
        return JsonResponse({'errors': account_form.errors}, status=400)

    account = domain.get_or_create_account(
        account_form.cleaned_data['email'],
        account_form.cleaned_data['account_number']
    )

    data = OrderedDict()
    for name, file in files_info.items():
        credential = domain.create_credential(account, name, verification_type)
        signed_url = domain.generate_presigned_s3_put_url(
            credential.s3_key, content_type=file['content_type'],
            content_MD5=file['content_md5'])
        data[name] = signed_url
    return JsonResponse(data)
