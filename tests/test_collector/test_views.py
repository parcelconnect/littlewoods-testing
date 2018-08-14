import json
import re
from collections import OrderedDict
from unittest import mock

import pytest
from django.urls import reverse

from idv.collector.models import Account, Credential


@pytest.fixture(autouse=True)
def aws_credentials(settings):
    settings.AWS_ACCESS_KEY = "AWS-TEST-KEY"
    settings.AWS_SECRET_KEY = "AWS-TEST-SECRET"
    return settings


class TestCollect:

    def test_json_context_normal(self, client):
        sign_s3_request_url = reverse('parametrized-collector:sign-s3-request',
                                      kwargs={'verification_type': 'normal'})
        response = client.get(reverse('collector:collect'))
        json_context = json.loads(response.context['json_context'])
        assert json_context['sign_s3_request_url'] == sign_s3_request_url

    def test_json_context_priority(self, client):
        sign_s3_request_url = reverse('parametrized-collector:sign-s3-request',
                                      kwargs={'verification_type': 'priority'})
        url = reverse('parametrized-collector:collect',
                      kwargs={'verification_type': 'priority'})
        response = client.get(url)
        json_context = json.loads(response.context['json_context'])
        assert json_context['sign_s3_request_url'] == sign_s3_request_url

    def test_returns_404_for_unknown_validation_type(self, client):
        url = reverse('parametrized-collector:collect',
                      kwargs={'verification_type': 'XXX'})
        response = client.get(url)
        assert response.status_code == 404


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
            'account_number': 'aa345678',
            'file_data': json.dumps({'filename': 'filetype'})
        })
        account = Account.objects.get()
        assert account.email == 'the@black.dog'
        assert account.account_number == 'aa345678'

    def test_retrieves_account_if_exists(self, client, account):
        url = reverse('collector:sign-s3-request')
        response = client.get(url, data={
            'email': 'account@littlewoods.ie',
            'account_number': '12345678',
            'file_data': json.dumps({'filename': 'filetype'})
        })
        assert Account.objects.count() == 1
        assert response.status_code == 200

    def test_creates_credentials(self, client, account_with_chars):
        url = reverse('collector:sign-s3-request')
        client.get(url, data={
            'email': 'account@littlewoods.ie',
            'account_number': '12ab5678',
            'file_data': json.dumps({
                'image.jpg': 'JPEG',
                'photo.png': 'PNG',
            })
        })
        creds = Credential.objects.filter(account=account_with_chars)
        assert creds.count() == 2

    def test_returns_404_for_unknown_validation_type(self, client, account):
        url = reverse('parametrized-collector:sign-s3-request',
                      kwargs={'verification_type': 'XXX'})
        response = client.get(url, data={
            'email': 'account@littlewoods.ie',
            'account_number': '12345678',
            'file_data': json.dumps(OrderedDict([('image.jpg', 'JPEG'),
                                                 ('photo.png', 'PNG')]))
        })
        assert response.status_code == 404

    @mock.patch("idv.common.aws.generate_presigned_s3_url")
    def test_returns_signed_urls(self, gen_mock, client, account):
        gen_mock.side_effect = ["XYZ", "ABC"]
        url = reverse('collector:sign-s3-request')
        response = client.get(url, data={
            'email': 'account@littlewoods.ie',
            'account_number': '12345678',
            'file_data': json.dumps(OrderedDict([('image.jpg', 'JPEG'),
                                                 ('photo.png', 'PNG')]))
        })
        cred1_s3_key = r'normal_12345678_\d+\.jpg'
        cred2_s3_key = r'normal_12345678_\d+\.png'

        assert len(gen_mock.call_args_list) == 2
        args1, kwargs1 = gen_mock.call_args_list[0]
        args2, kwargs2 = gen_mock.call_args_list[1]
        assert re.match(cred1_s3_key, args1[2])
        assert re.match(cred2_s3_key, args2[2])
        assert kwargs1['ContentType'] == 'JPEG'
        assert kwargs2['ContentType'] == 'PNG'

        assert Credential.objects.get(original_filename='image.jpg')
        assert Credential.objects.get(original_filename='photo.png')

        content = json.loads(response.content.decode())
        assert content['image.jpg'] == "XYZ"
        assert content['photo.png'] == "ABC"

    @mock.patch("idv.common.aws.generate_presigned_s3_url")
    def test_returns_signed_urls_for_priority(self, gen_mock, client, account):
        gen_mock.side_effect = ["XYZ", "ABC"]
        url = reverse('parametrized-collector:sign-s3-request',
                      kwargs={'verification_type': 'priority'})
        response = client.get(url, data={
            'email': 'account@littlewoods.ie',
            'account_number': '12345678',
            'file_data': json.dumps(OrderedDict([('image.jpg', 'JPEG'),
                                                 ('photo.png', 'PNG')]))
        })
        cred1_s3_key = r'priority_12345678_\d+\.jpg'
        cred2_s3_key = r'priority_12345678_\d+\.png'

        assert len(gen_mock.call_args_list) == 2
        args1, kwargs1 = gen_mock.call_args_list[0]
        args2, kwargs2 = gen_mock.call_args_list[1]
        assert re.match(cred1_s3_key, args1[2])
        assert re.match(cred2_s3_key, args2[2])
        assert kwargs1['ContentType'] == 'JPEG'
        assert kwargs2['ContentType'] == 'PNG'

        assert Credential.objects.get(original_filename='image.jpg')
        assert Credential.objects.get(original_filename='photo.png')

        content = json.loads(response.content.decode())
        assert content['image.jpg'] == "XYZ"
        assert content['photo.png'] == "ABC"
