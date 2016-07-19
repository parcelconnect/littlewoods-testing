import pytest
from mock import patch

from django.conf import settings

from idv.collector.domain import (
    create_credential, generate_presigned_s3_url, get_or_create_account)


@pytest.mark.django_db
class TestGetOrCreateAccount:

    def test_account_creation(self):
        account = get_or_create_account('i.am.not@that.innocent', '12345678')
        assert account.pk is not None
        assert account.account_number == '12345678'
        assert account.email == 'i.am.not@that.innocent'

    def test_account_retrieval(self, account):
        acc = get_or_create_account('account@littlewoods', '12345678')
        assert account.pk == acc.pk


@pytest.mark.django_db
class TestCredentialCreation:

    def test_consecutive_s3_filename_generation(self, account):
        cred1 = create_credential(account, 'awesome.jpg')
        cred2 = create_credential(account, 'sexy.jpg')
        assert cred1.s3_key.endswith('12345678_1.jpg')
        assert cred2.s3_key.endswith('12345678_2.jpg')


class TestPreseignedS3UrlGeneration:

    @patch('idv.common.aws.generate_presigned_s3_url')
    def test_parameters(self, generation_func_mock):
        settings.S3_BUCKET = 'BUCK'
        generate_presigned_s3_url('cooking', 'json')
        generation_func_mock.assert_called_once_with(
            'put_object', 'BUCK', 'cooking', ContentType='json')
