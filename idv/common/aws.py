import botocore
import boto3

from django.conf import settings


class S3KeyNotFoundError(Exception):
    pass


def get_boto_credentials_from_settings():
    return {
        'aws_access_key_id': settings.AWS_ACCESS_KEY,
        'aws_secret_access_key': settings.AWS_SECRET_KEY
    }


def get_s3_client(credentials=None):
    if credentials is None:
        credentials = get_boto_credentials_from_settings()
    return boto3.client('s3', **credentials)


def generate_presigned_s3_url(client_method, bucket, key,
                              client=None, expires_in=5*60, **params):
    if client is None:
        client = get_s3_client()

    params.update({
        'Bucket': settings.S3_BUCKET,
        'Key': key,
    })
    return client.generate_presigned_url(
        ClientMethod=client_method,
        ExpiresIn=expires_in,
        Params=params
    )


def get_exception_status_code(exception):
    return exception.response['Error']['Code']


def download_file(bucket, s3_key, local_path, client=None):
    if client is None:
        client = get_s3_client()

    try:
        return client.download_file(bucket, s3_key, local_path)
    except botocore.exceptions.ClientError as exc:
        if get_exception_status_code(exc) == '404':
            raise S3KeyNotFoundError
