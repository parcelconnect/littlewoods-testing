from unittest.mock import patch

import pytest

from idv.collector.domain import (
    create_credential, generate_presigned_s3_put_url, get_or_create_account,
    has_whitelisted_extension)


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
        cred1 = create_credential(account, 'awesome.jpg', 'normal')
        cred2 = create_credential(account, 'sexy.jpg', 'normal')
        assert cred1.s3_key == 'normal_12345678_1.jpg'
        assert cred2.s3_key == 'normal_12345678_2.jpg'

    def test_consecutive_s3_filename_generation_for_priority(self, account):
        cred1 = create_credential(account, 'awesome.jpg', 'priority')
        cred2 = create_credential(account, 'sexy.jpg', 'priority')
        assert cred1.s3_key == 'priority_12345678_1.jpg'
        assert cred2.s3_key == 'priority_12345678_2.jpg'

    def test_marked_as_blocked_if_blocked_extension(self, account):
        cred = create_credential(account, 'awesome.exe', 'normal')
        assert cred.is_blocked is True


class TestPreseignedS3UrlGeneration:

    @patch('idv.common.aws.generate_presigned_s3_url')
    def test_parameters(self, generation_func_mock, settings):
        assert generate_presigned_s3_put_url('cat', 'json', 'X') is not None
        generation_func_mock.assert_called_once_with(
            'put_object', 'BUCK', 'cat', ContentType='json',
            ContentMD5='X')

    def test_no_settings_returns_none(self, settings):
        settings.S3_BUCKET = None
        assert generate_presigned_s3_put_url('cooking', 'json', 'X') is None


@pytest.mark.django_db
class TestWhitelistedExtensions:

    def test_whitelisted_lowercase_extension(self, account):
        cred = create_credential(account, 'file.jpg', 'normal')
        assert has_whitelisted_extension(cred) is True

    def test_whitelisted_mixedcase_extension(self, account):
        cred = create_credential(account, 'fILe.pNg', 'normal')
        assert has_whitelisted_extension(cred) is True

    def test_non_whitelisted_mixedcase_extension(self, account):
        cred = create_credential(account, 'file.exE', 'normal')
        assert has_whitelisted_extension(cred) is False

    def test_missing_extension(self, account):
        cred = create_credential(account, 'file', 'normal')
        assert has_whitelisted_extension(cred) is False
