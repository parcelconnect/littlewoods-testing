import logging
import os

from django.conf import settings

from idv.common import aws
from idv.sftp import domain as sftp_domain
from idv.sftp.models import SftpAccount
from idv.sftp.proxy.http import HttpProxy

from .models import MoveCommandStatus

logger = logging.getLogger(__name__)


def get_http_proxy_from_settings():
    if settings.HTTP_PROXY['host']:
        return HttpProxy(**settings.HTTP_PROXY)
    return None


def move_credential_files(credentials):
    aws_client = aws.get_s3_client()
    sftp = SftpAccount.objects.get()
    http_proxy = get_http_proxy_from_settings()

    with sftp_domain.sftp_client_from_model(sftp, http_proxy) as sftp_client:
        for cred in credentials:
            logger.info("Start moving {}".format(cred))
            try:
                move_credential_file(cred, aws_client, sftp_client, sftp)
            except aws.S3KeyNotFoundError:
                continue
            logger.info("{} moved".format(cred))


def move_credential_file(credential, aws_client, sftp_client, sftp_account,
                         local_tmp_dir='/tmp'):
    local_path = os.path.join(local_tmp_dir, credential.s3_key)
    try:
        aws.download_file(settings.S3_BUCKET, credential.s3_key, local_path)
    except aws.S3KeyNotFoundError:
        credential.mark_as_not_found()
        logger.info("{} not found in S3".format(credential))
        raise
    logger.info("Downloaded {} to {}".format(credential, local_path))
    credential.mark_as_found()

    remote_dir = _get_sftp_credential_dir(sftp_account, credential)
    if not sftp_domain.path_exists(sftp_client, remote_dir):
        sftp_client.mkdir(remote_dir)
        logger.info("Created directory {}".format(remote_dir))

    remote_path = os.path.join(remote_dir, credential.s3_key)
    sftp_client.put(local_path, remote_path)
    logger.info("Uploaded {} to {}".format(local_path, remote_path))
    credential.mark_as_copied()

    aws_client.delete_object(Bucket=settings.S3_BUCKET, Key=credential.s3_key)
    logger.info("Deleted {} from S3".format(credential.s3_key))
    credential.mark_as_moved()


def _get_sftp_credential_dir(sftp_account, credential):
    container_dir = credential.created_at.strftime("%Y%m%d")
    if credential.is_blocked:
        container_dir = '{}-blocked'.format(container_dir)
    return os.path.join(sftp_account.base_path, container_dir)


def get_last_move_checkpoint():
    try:
        status = MoveCommandStatus.objects.get()
    except MoveCommandStatus.DoesNotExist:
        return None
    return status.checkpoint
