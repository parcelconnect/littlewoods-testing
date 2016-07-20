import json
import re

import pytest

from django.core.urlresolvers import reverse

from idv.collector.models import Account, Credential


class TestCollect:

    def test_json_context(self, client):
        sign_s3_request_url = reverse('collector:sign-s3-request')
        response = client.get(reverse('collector:collect'))
        json_context = json.loads(response.context['json_context'])
        assert json_context['sign_s3_request_url'] == sign_s3_request_url


@pytest.mark.django_db
class TestSignS3Request:

    def test_returns_400_if_account_data_invalid(self, client):
        url = reverse('collector:sign-s3-request')
        response = client.get(url, data={
            'email': 'oops',
            'account_number': '12345678',
            'file_data': json.dumps({'filename': 'filetype'})
        })
        assert response.status_code == 400

    def test_returns_errors_if_account_data_invalid(self, client):
        url = reverse('collector:sign-s3-request')
        response = client.get(url, data={
            'email': 'oops',
            'account_number': '1234567812',
            'file_data': json.dumps({'filename': 'filetype'})
        })
        content = json.loads(response.content.decode())
        assert 'email' in content['errors']
        assert 'account_number' in content['errors']

    def test_creates_account_if_not_found(self, client):
        url = reverse('collector:sign-s3-request')
        client.get(url, data={
            'email': 'the@black.dog',
            'account_number': '12345678',
            'file_data': json.dumps({'filename': 'filetype'})
        })
        account = Account.objects.get()
        assert account.email == 'the@black.dog'
        assert account.account_number == '12345678'

    def test_retrieves_account_if_exists(self, client, account):
        url = reverse('collector:sign-s3-request')
        response = client.get(url, data={
            'email': 'account@littlewoods.ie',
            'account_number': '12345678',
            'file_data': json.dumps({'filename': 'filetype'})
        })
        assert Account.objects.count() == 1
        assert response.status_code == 200

    def test_creates_credentials(self, client, account):
        url = reverse('collector:sign-s3-request')
        client.get(url, data={
            'email': 'account@littlewoods.ie',
            'account_number': '12345678',
            'file_data': json.dumps({
                'image.jpg': 'JPEG',
                'photo.png': 'PNG',
            })
        })
        assert Credential.objects.filter(account=account).count() == 2

    def test_returns_signed_urls(self, client, account):
        url = reverse('collector:sign-s3-request')
        response = client.get(url, data={
            'email': 'account@littlewoods.ie',
            'account_number': '12345678',
            'file_data': json.dumps({
                'image.jpg': 'JPEG',
                'photo.png': 'PNG',
            })
        })
        cred1 = Credential.objects.get(original_filename='image.jpg')
        cred2 = Credential.objects.get(original_filename='photo.png')

        url_regexp = 'https://.*amazon.*{}.*'
        cred1_url_re = url_regexp.format(cred1.s3_key)
        cred2_url_re = url_regexp.format(cred2.s3_key)

        content = json.loads(response.content.decode())
        assert re.match(cred1_url_re, content['image.jpg']) is not None
        assert re.match(cred2_url_re, content['photo.png']) is not None
