import logging
import os

from django.conf import settings

from idv.common import aws
from idv.sftp.domain import sftp_client_from_model
from idv.sftp.models import SftpAccount
from idv.sftp.proxy.http import HttpProxy

logger = logging.getLogger(__name__)


def get_http_proxy_from_settings():
    if settings.HTTP_PROXY['host'] is not None:
        return HttpProxy(**settings.HTTP_PROXY)
    return None


def move_credential_files(credentials):
    aws_client = aws.get_s3_client()
    sftp_account = SftpAccount.objects.get()
    http_proxy = get_http_proxy_from_settings()

    with sftp_client_from_model(sftp_account, http_proxy) as sftp_client:
        for cred in credentials:
            logger.info("Start moving {}".format(cred))
            move_credential_file(cred, aws_client, sftp_client, sftp_account)
            logger.info("{} moved".format(cred))


def move_credential_file(credential, aws_client, sftp_client, sftp_account,
                         local_tmp_dir='/tmp'):
    local_path = os.path.join(local_tmp_dir, credential.s3_key)
    aws_client.download_file(settings.S3_BUCKET, credential.s3_key, local_path)
    logger.info("Downloaded {} to {}".format(credential, local_path))
    credential.mark_as_found()

    remote_path = os.path.join(sftp_account.base_path, credential.s3_key)
    sftp_client.put(local_path, remote_path)
    logger.info("Uploaded {} to {}".format(local_path, remote_path))
    credential.mark_as_copied()

    aws_client.delete_object(Bucket=settings.S3_BUCKET, Key=credential.s3_key)
    logger.info("Deleted {} from S3".format(credential.s3_key))
    credential.mark_as_moved()
