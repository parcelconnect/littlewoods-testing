import boto3

from django.conf import settings


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
                              client=None, expires_in=30, **params):
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
