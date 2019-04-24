import pytest
from celery.contrib.testing.tasks import ping
from celery.result import allow_join_result
from freezegun import freeze_time

import idv.celery
from idv.collector import domain as collector_domain
from idv.collector.const import CredentialStatus
from idv.sftp.models import SftpAccount


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
    cred = collector_domain.create_credential(account, 'unchecked.jpg',
                                              'normal')
    cred.status = CredentialStatus.Unchecked.value
    cred.save()
    return cred


@pytest.fixture
@freeze_time('2016-01-03 12:00')
def found_credential(account):
    cred = collector_domain.create_credential(account, 'found.jpg', 'normal')
    cred.status = CredentialStatus.Found.value
    cred.save()
    return cred


@pytest.fixture
@freeze_time('2016-01-04 12:00')
def not_found_credential(account):
    cred = collector_domain.create_credential(account, 'not_found.jpg',
                                              'normal')
    cred.status = CredentialStatus.NotFound.value
    cred.save()
    return cred


@pytest.fixture
@freeze_time('2016-01-02 12:00')
def blocked_credential(account):
    return collector_domain.create_credential(account, 'blocked.exe', 'normal')


@pytest.fixture
@freeze_time('2016-01-05 12:00')
def copied_credential(account):
    cred = collector_domain.create_credential(account, 'copied.jpg', 'normal')
    cred.status = CredentialStatus.Copied.value
    cred.save()
    return cred


@pytest.fixture
@freeze_time('2016-01-06 12:00')
def moved_credential(account):
    cred = collector_domain.create_credential(account, 'moved.jpg', 'normal')
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


@pytest.fixture
def accounts(account, account_with_chars, other_account):
    return [
        account,
        account_with_chars,
        other_account
    ]


@pytest.fixture
def settings(settings):
    settings.AWS_ACCESS_KEY = 'TEST-KEY'
    settings.AWS_SECRET_KEY = 'TEST-SECRET-KEY'
    settings.S3_BUCKET = 'BUCK'
    return settings


def wait_for_ping(ping_task_timeout=10.0):
    """
    Wait for the celery worker to respond to a ping.
    This should ensure that any other running tasks are done.
    """
    with allow_join_result():
        assert ping.delay().get(timeout=ping_task_timeout) == 'pong'


@pytest.fixture
def celery_memory_settings(settings):
    settings.BROKER_URL = 'memory://'
    settings.CELERY_RESULT_BACKEND = 'cache+memory://'


@pytest.fixture
def celery_app(celery_memory_settings):
    return idv.celery.app


@pytest.fixture
def sftp_account():
    return SftpAccount.objects.create(
        host='127.0.0.1',
        port='22',
        username='maxpayne',
        password='1234',
        base_path='/some_path',
    )
