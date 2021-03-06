import logging
import os.path
from datetime import date

from django.conf import settings
from django.db import transaction

from idv.common import aws

from .models import Account, AccountCredentialIndex, Credential

logger = logging.getLogger(__name__)


@transaction.atomic
def get_or_create_account(email, account_number, date_1=date.min, date_2=date.min):  # noqa
    """
    Get or create a new `idv.collector.models.Account` object.
    If object already exists, we override dates values with given ones.
    When a new one is created, it also creates an `idv.collector.models.
    AccountCredentialIndex` object responsible for generating unique
    credential indices for each account.

    Args:
        email (str): User email used in Littlewoods
        account_number (str): Account number in Littlewoods
        date_1 (date): Issued date for proof of address 1 file
        date_2 (date): Issued date for proof of address 2 file
    Returns:
        idv.collector.models.Account obj
    """
    try:
        account = Account.objects.get(account_number=account_number)
        account.proof_of_address_date_1 = date_1
        account.proof_of_address_date_2 = date_2
        account.save()
    except Account.DoesNotExist:
        account = Account(email=email, account_number=account_number,
                          proof_of_address_date_1=date_1,
                          proof_of_address_date_2=date_2)

        account.save()
        AccountCredentialIndex.objects.create(account=account)
    return account


@transaction.atomic
def create_credential(account, filename, verification_type):
    """
    Create an `idv.collector.models.Credential` object by using
    `idv.collector.models.AccountCredentialIndex` to generate a unique s3 key.

    Args:
        account (idv.collector.models.Account): Account to create
                                                credential for
        filename (str): The filename of the original file the user wants to
                        upload. Not used anywhere, just stored for debugging
                        purposes in the future, if any.
        verification_type (str): The type of verification
    Returns:
        idv.collector.models.Credential obj

    """
    s3_key = _generate_s3_key(account, filename, verification_type)
    credential = Credential.objects.create(
        account=account,
        original_filename=filename,
        s3_key=s3_key
    )
    if not has_whitelisted_extension(credential):
        credential.mark_as_blocked()
    return credential


def _generate_s3_key(account, filename, verification_type):
    _, extension = os.path.splitext(filename)
    file_index = AccountCredentialIndex.next(account)
    s3_key_fmt = '{verification_type}_{account_number}_{file_index}{extension}'
    s3_key = s3_key_fmt.format(
        account_number=account.account_number,
        file_index=file_index,
        extension=extension,
        verification_type=verification_type
    )
    return s3_key


def generate_presigned_s3_put_url(s3_key, content_type, content_MD5):
    """
    Generates a presigned s3 'put_object' url for given key
    Args:
        s3_key (str): The s3 key we want to generate the signed url for
        content_type (str): The type of the file
        content_MD5 (str): The MD5 of the file
    Returns:
        str: A presigned s3 url
    """
    if (not settings.AWS_ACCESS_KEY or not settings.AWS_SECRET_KEY or
            not settings.S3_BUCKET):
        # Raise exception to get a notification on
        logger.exception('No AWS settings found!')
        return None
    return aws.generate_presigned_s3_url(
        'put_object', settings.S3_BUCKET, s3_key, ContentType=content_type,
        ContentMD5=content_MD5
    )


def has_whitelisted_extension(credential):
    filename, extension = os.path.splitext(credential.original_filename)
    # remove dot from extension
    extension = extension[1:]
    return extension.lower() in settings.WHITELISTED_EXTENSIONS
