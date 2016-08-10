import pytest
from freezegun import freeze_time

from idv.collector import domain as collector_domain
from idv.collector.const import CredentialStatus


@pytest.fixture
@freeze_time('2016-01-01 00:00')
def account():
    return collector_domain.get_or_create_account(
        email='account@littlewoods.ie',
        account_number='12345678'
    )


@pytest.fixture
@freeze_time('2016-01-01 00:00')
def account_with_chars():
    return collector_domain.get_or_create_account(
        email='account@littlewoods.ie',
        account_number='12ab5678'
    )


@pytest.fixture
@freeze_time('2016-01-01 00:00')
def other_account():
    return collector_domain.get_or_create_account(
        email='other.account@littlewoods.ie',
        account_number='12341234'
    )


@pytest.fixture
@freeze_time('2016-01-02 12:00')
def unchecked_credential(account):
    cred = collector_domain.create_credential(account, 'unchecked.jpg')
    cred.status = CredentialStatus.Unchecked.value
    cred.save()
    return cred


@pytest.fixture
@freeze_time('2016-01-03 12:00')
def found_credential(account):
    cred = collector_domain.create_credential(account, 'found.jpg')
    cred.status = CredentialStatus.Found.value
    cred.save()
    return cred


@pytest.fixture
@freeze_time('2016-01-04 12:00')
def not_found_credential(account):
    cred = collector_domain.create_credential(account, 'not_found.jpg')
    cred.status = CredentialStatus.NotFound.value
    cred.save()
    return cred


@pytest.fixture
@freeze_time('2016-01-02 12:00')
def blocked_credential(account):
    cred = collector_domain.create_credential(account, 'blocked.jpg')
    cred.status = CredentialStatus.Blocked.value
    cred.save()
    return cred


@pytest.fixture
@freeze_time('2016-01-05 12:00')
def copied_credential(account):
    cred = collector_domain.create_credential(account, 'copied.jpg')
    cred.status = CredentialStatus.Copied.value
    cred.save()
    return cred


@pytest.fixture
@freeze_time('2016-01-06 12:00')
def moved_credential(account):
    cred = collector_domain.create_credential(account, 'moved.jpg')
    cred.status = CredentialStatus.Moved.value
    cred.save()
    return cred


@pytest.fixture
def credentials(unchecked_credential, found_credential, not_found_credential,
                copied_credential, moved_credential, blocked_credential):
    return [
        unchecked_credential,
        found_credential,
        not_found_credential,
        copied_credential,
        moved_credential,
        blocked_credential,
    ]
