import datetime

import pytest
from freezegun import freeze_time

from idv.collector.const import CredentialStatus
from idv.collector.domain import create_credential
from idv.collector.models import Credential


@pytest.mark.django_db
class TestCredentialQuerysets:

    def test_need_moving_query(self, moved_credential, credentials):
        credentials = Credential.objects.need_moving().order_by('status')
        assert len(credentials) == 3
        assert credentials[0].status == CredentialStatus.Unchecked.value
        assert credentials[1].status == CredentialStatus.Unchecked.value
        assert credentials[2].status == CredentialStatus.Found.value

    def test_created_betwen_query(self, moved_credential, credentials):
        since = datetime.datetime(2016, 1, 3)
        until = datetime.datetime(2016, 1, 5)
        date_range = (since, until)
        credentials = Credential.objects.created_between(date_range)
        credentials = credentials.order_by('created_at')
        assert len(credentials) == 2
        assert credentials[0].status == CredentialStatus.Found.value
        assert credentials[1].status == CredentialStatus.NotFound.value

    def test_not_found_query(self, account, credentials):
        cred = create_credential(account, 'asdf.jpg', 'normal')
        cred.status = CredentialStatus.NotFound.value
        cred.save()

        not_found = Credential.objects.not_found()
        assert not_found.count() == 2
        assert not_found[0].status == CredentialStatus.NotFound.value
        assert not_found[1].status == CredentialStatus.NotFound.value

    def test_moved_query(self, account, credentials):
        cred = create_credential(account, 'asdf.jpg', 'normal')
        cred.status = CredentialStatus.Moved.value
        cred.save()

        moved = Credential.objects.moved()
        assert moved.count() == 2
        assert moved[0].status == CredentialStatus.Moved.value
        assert moved[1].status == CredentialStatus.Moved.value

    def test_blocked_query(self, account, credentials):
        cred = create_credential(account, 'asdf.jpg', 'normal')
        cred.mark_as_blocked()

        blocked = Credential.objects.blocked()
        assert blocked.count() == 2
        assert blocked[0].is_blocked is True
        assert blocked[1].is_blocked is True


@pytest.mark.django_db
class TestCredentials:

    def test_marks_as_found(self, unchecked_credential):
        unchecked_credential.mark_as_found()
        unchecked_credential.refresh_from_db()
        assert unchecked_credential.status == CredentialStatus.Found.value

    def test_marks_as_not_found(self, unchecked_credential):
        unchecked_credential.mark_as_not_found()
        unchecked_credential.refresh_from_db()
        assert unchecked_credential.status == CredentialStatus.NotFound.value

    @freeze_time('2016-02-01 02:00:00')
    def test_marks_as_copied(self, found_credential):
        found_credential.mark_as_copied()
        found_credential.refresh_from_db()
        assert found_credential.status == CredentialStatus.Copied.value
        assert found_credential.copied_at.year == 2016
        assert found_credential.copied_at.month == 2
        assert found_credential.copied_at.day == 1
        assert found_credential.copied_at.hour == 2

    @freeze_time('2016-02-01 02:00:00')
    def test_marks_as_moved(self, copied_credential):
        copied_credential.mark_as_moved()
        copied_credential.refresh_from_db()
        assert copied_credential.status == CredentialStatus.Moved.value
        assert copied_credential.deleted_at.year == 2016
        assert copied_credential.deleted_at.month == 2
        assert copied_credential.deleted_at.day == 1
        assert copied_credential.deleted_at.hour == 2

    @freeze_time('2016-02-01 02:00:00')
    def test_marks_as_blocked(self, found_credential):
        found_credential.mark_as_blocked()
        found_credential.refresh_from_db()
        assert found_credential.is_blocked is True
