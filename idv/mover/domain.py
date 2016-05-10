import logging
import os

from django.conf import settings

from idv.common import aws
from idv.common.sftp import get_sftp_client_from_model

from .models import SftpAccount

logger = logging.getLogger(__name__)


def move_credential_files(credentials):
    sftp_config = SftpAccount.objects.get()
    aws_client = aws.get_s3_client()

    for credential in credentials:
        logger.info("Start moving {}".format(credential))
        move_credential_file(credential, aws_client, sftp_config)
        credential.mark_as_deleted()
        logger.info("{} marked as deleted".format(credential))
        logger.info("{} moved {}".format(credential))


def move_credential_file(credential, aws_client, sftp_config,
                         local_tmp_dir='/tmp'):
    local_path = os.path.join(local_tmp_dir, credential.s3_key)
    aws_client.download_file(settings.S3_BUCKET, credential.s3_key, local_path)
    logger.info("Downloaded {} to {}".format(credential, local_path))

    remote_path = os.path.join(sftp_config.base_path, credential.s3_key)
    with get_sftp_client_from_model(sftp_config) as client:
        client.put(local_path, remote_path)
    logger.info("Uploaded {} to {}".format(local_path, remote_path))

    aws_client.delete_object(Bucket=settings.S3_BUCKET, Key=credential.s3_key)
