import os.path

from django.db import transaction

from .models import Account, AccountCredentialIndex, Credential


@transaction.atomic
def get_or_create_account(email, account_number):
    try:
        account = Account.objects.get(account_number=account_number)
    except Account.DoesNotExist:
        account = Account(email=email, account_number=account_number)
        account.save()
        AccountCredentialIndex.objects.create(account=account)
    return account


@transaction.atomic
def create_credential(account, filename):
    s3_key = _generate_s3_key(account, filename)
    return Credential.objects.create(
        account=account,
        original_filename=filename,
        s3_key=s3_key
    )


def _generate_s3_key(account, filename):
    _, extension = os.path.splitext(filename)
    file_index = AccountCredentialIndex.next(account)
    s3_key = '{account_number}_{file_index}{extension}'.format(
        account_number=account.account_number,
        file_index=file_index,
        extension=extension
    )
    return s3_key
