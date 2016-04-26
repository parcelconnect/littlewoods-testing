import boto3

from django.conf import settings


def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY
    )


def generate_presigned_s3_url(client_method, key, expires_in=30, **params):
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
