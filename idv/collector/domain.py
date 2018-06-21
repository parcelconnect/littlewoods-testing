import os.path

from django.conf import settings
from django.db import transaction

from idv.common import aws

from .models import Account, AccountCredentialIndex, Credential


@transaction.atomic
def get_or_create_account(email, account_number):
    """
    Get or create a new `idv.collector.models.Account` object.
    When a new one is created, it also creates an `idv.collector.models.
    AccountCredentialIndex` object responsible for generating unique credential
    indices for each account.

    Args:
        email (str): User email used in Littlewoods
        account_number (str): Account number in Littlewoods
    Returns:
        idv.collector.models.Account obj

    """
    try:
        account = Account.objects.get(account_number=account_number)
    except Account.DoesNotExist:
        account = Account(email=email, account_number=account_number)
        account.save()
        AccountCredentialIndex.objects.create(account=account)
    return account


@transaction.atomic
def create_credential(account, filename):
    """
    Create an `idv.collector.models.Credential` object by using
    `idv.collector.models.AccountCredentialIndex` to generate a unique s3 key.

    Args:
        account (idv.collector.models.Account): Account to create
                                                credential for
        filename (str): The filename of the original file the user wants to
                        upload. Not used anywhere, just stored for debugging
                        purposes in the future, if any.
    Returns:
        idv.collector.models.Credential obj

    """
    s3_key = _generate_s3_key(account, filename)
    credential = Credential.objects.create(
        account=account,
        original_filename=filename,
        s3_key=s3_key
    )
    if not has_whitelisted_extension(credential):
        credential.mark_as_blocked()
    return credential


def _generate_s3_key(account, filename):
    _, extension = os.path.splitext(filename)
    file_index = AccountCredentialIndex.next(account)
    s3_key = '{account_number}_{file_index}{extension}'.format(
        account_number=account.account_number,
        file_index=file_index,
        extension=extension
    )
    return s3_key


def generate_presigned_s3_url(s3_key, filetype):
    """
    Args:
        s3_key (str): The s3 key we want to generate the signed url for
        filetype (str): The type of the file we want to generate the
                        signed url for
    Returns:
        str: A presigned s3 url
    """
    return aws.generate_presigned_s3_url(
        'put_object', settings.S3_BUCKET, s3_key, ContentType=filetype)


def has_whitelisted_extension(credential):
    filename, extension = os.path.splitext(credential.original_filename)
    # remove dot from extension
    extension = extension[1:]
    return extension.lower() in settings.WHITELISTED_EXTENSIONS
