import os

import pytest
from django.test import TestCase, override_settings
from moto import mock_s3

from idv.common.aws import S3KeyNotFoundError, download_file, get_s3_client


@override_settings(AWS_ACCESS_KEY='foo', AWS_SECRET_KEY='bar')
class TestAWS(TestCase):

    @mock_s3
    def test_download_file_returns_expected_file(self):
        bucket = 'mybucket'
        key = 'mykey'
        upload_filename = 'upload.txt'
        download_filename = 'download.txt'
        body = b'Los Pollos Hermanos'

        with open(upload_filename, 'wb') as uploaded_file:
            uploaded_file.write(body)

        client = get_s3_client()
        client.create_bucket(Bucket=bucket)
        client.upload_file(Filename=upload_filename, Bucket=bucket, Key=key)

        download_file(bucket, key, download_filename)

        with open(download_filename, 'rb') as downloaded_file:
            content = downloaded_file.readlines()[0]

        os.remove(upload_filename)
        os.remove(download_filename)

        assert content == body

    @mock_s3
    def test_raises_exception_when_key_not_found(self):
        bucket = 'mybucket'
        key = 'mykey'

        client = get_s3_client()
        client.create_bucket(Bucket=bucket)

        with pytest.raises(S3KeyNotFoundError):
            download_file(bucket, key, 'invalid', client=client)
