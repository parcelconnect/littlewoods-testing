from unittest.mock import Mock, patch

import pytest
from django.test import TestCase, override_settings
from freezegun import freeze_time

from idv.collector.const import CredentialStatus
from idv.common.aws import S3KeyNotFoundError
from idv.mover import domain
from idv.mover.commands import move
from idv.sftp.proxy.http import HttpProxy


@pytest.mark.django_db
class TestMoveCheckpoint:

    def test_returns_none_if_no_checkpoint(self):
        assert domain.get_last_move_checkpoint() is None

    @freeze_time('2016-02-01 01:02:03')
    @patch('idv.mover.commands.move_credential_files')
    def test_returns_checkpoint(self, move_creds_mock):
        move()
        checkpoint = domain.get_last_move_checkpoint()
        assert checkpoint.year == 2016
        assert checkpoint.month == 2
        assert checkpoint.day == 1
        assert checkpoint.hour == 1
        assert checkpoint.minute == 2
        assert checkpoint.second == 3


class TestGetHttpProxyFromSettings(TestCase):

    def test_returns_none_if_no_settings(self):
        assert domain.get_http_proxy_from_settings() is None

    @override_settings(HTTP_PROXY={
        'host': '91.123.12.45',
        'port': '8080',
        'username': 'Username',
        'password': 'Password',
    })
    def test_returns_http_proxy_when_settings_set(self):
        http_proxy = domain.get_http_proxy_from_settings()

        assert http_proxy is not None
        assert isinstance(http_proxy, HttpProxy) is True


@pytest.mark.django_db
class TestMoveCredentialFiles:

    @patch('paramiko.SFTPClient', autospec=True)
    @patch('paramiko.Transport', autospec=True)
    @patch('idv.sftp.domain.store_host_key_data')
    @patch('idv.mover.domain.move_credential_file')
    def test_invokes_move_credential_file_once_per_credential(
            self, mock_move_method, mock_sftp_method, mock_transport,
            mock_sftp, sftp_account, credentials):
        mock_move_method.side_effect = [
            None, None, S3KeyNotFoundError(), None, None, None]

        domain.move_credential_files(credentials)

        assert mock_move_method.call_count == len(credentials)


@pytest.mark.django_db
class TestMoveCredentialFile:

    @patch('idv.common.aws.download_file')
    def test_raises_exception_and_mark_credential_as_not_found_when_s3_key_not_found(  # noqa
            self, mock_download_file, unchecked_credential):
        assert unchecked_credential.status != CredentialStatus.NotFound.value

        mock_download_file.side_effect = S3KeyNotFoundError()

        with pytest.raises(S3KeyNotFoundError):
            domain.move_credential_file(unchecked_credential, None, None, None)

        assert unchecked_credential.status == CredentialStatus.NotFound.value

    @patch('paramiko.SFTPClient', autospec=True)
    @patch('boto3.client', autospec=True)
    @patch('idv.common.aws.download_file')
    def test_mark_as_moved_when_credentials_successfully_moved(
            self, mock_download_file, mock_aws, mock_sftp,
            unchecked_credential, sftp_account):
        assert unchecked_credential.status != CredentialStatus.Moved.value

        mock_aws.delete_object = Mock()
        mock_sftp.stat.side_effect = IOError(2, 'Not a directory')

        domain.move_credential_file(
            unchecked_credential, mock_aws, mock_sftp, sftp_account)

        assert unchecked_credential.status == CredentialStatus.Moved.value


@pytest.mark.django_db
class TestGetSftpCredentialDir:

    def test_returns_blocked_path_when_credential_is_blocked(
            self, blocked_credential, sftp_account):
        dir = domain._get_sftp_credential_dir(sftp_account, blocked_credential)

        assert dir.endswith('-blocked')

    def test_returns_normal_path_when_credential_is_unblocked(
            self, found_credential, sftp_account):
        dir = domain._get_sftp_credential_dir(sftp_account, found_credential)

        assert not dir.endswith('-blocked')
