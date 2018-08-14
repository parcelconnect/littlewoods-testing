from datetime import datetime

import pytest
from freezegun import freeze_time

from idv.collector.const import CredentialStatus
from idv.collector.domain import create_credential
from idv.collector.models import Credential
from idv.mover.reporting import report_csv


@pytest.mark.django_db
class TestReportCsv:

    def test_headers(self, credentials):
        date_range = (
            datetime(2016, 1, 2),
            datetime(2016, 1, 6)
        )
        with report_csv(date_range) as fd:
            content = fd.getvalue()
        content_lines = content.split()
        content_headers = content_lines[0]
        assert content_headers == ('"account_number","email","files_moved",'
                                   '"files_not_found","files_blocked"')

    def test_creation_date_filtering(self, credentials, other_account):
        with freeze_time('2016-01-10'):
            cred = create_credential(other_account, 'moved.jpg', 'normal')
            cred.status = CredentialStatus.Moved.value
            cred.save()

            cred = create_credential(other_account, 'not_found.jpg', 'normal')
            cred.status = CredentialStatus.NotFound.value
            cred.save()

        date_range = (
            datetime(2016, 1, 1),
            datetime(2016, 1, 7)
        )
        with report_csv(date_range) as fd:
            report = fd.getvalue()

        report_lines = report.split()
        assert len(report_lines) == 2
        assert report_lines[1].startswith('"12345678"')

    def test_lists_moved(self, credentials, account):
        with freeze_time('2016-01-04'):
            cred = create_credential(account, 'moved-away.jpg', 'normal')
            cred.status = CredentialStatus.Moved.value
            cred.save()

        date_range = (
            datetime(2016, 1, 1),
            datetime(2016, 1, 10)
        )
        with report_csv(date_range) as fd:
            report = fd.getvalue()

        moved = Credential.objects.moved()
        moved = sorted(moved.values_list('s3_key', flat=True))

        report_lines = report.split()
        assert len(report_lines) == 2
        assert '"{},{}"'.format(*moved) in report_lines[1]

    def test_lists_not_found(self, not_found_credential, account):
        with freeze_time('2016-01-04'):
            cred = create_credential(account, 'not--found.jpg', 'normal')
            cred.status = CredentialStatus.NotFound.value
            cred.save()

        date_range = (
            datetime(2016, 1, 1),
            datetime(2016, 1, 10)
        )
        with report_csv(date_range) as fd:
            report = fd.getvalue()

        not_found = Credential.objects.not_found()
        not_found = sorted(not_found.values_list('s3_key', flat=True))

        report_lines = report.split()
        assert len(report_lines) == 2
        assert '"{},{}"'.format(*not_found) in report_lines[1]

    def test_lists_blocked(self, blocked_credential, account):
        with freeze_time('2016-01-04'):
            create_credential(account, 'blocked2.exe', 'normal')

        date_range = (
            datetime(2016, 1, 1),
            datetime(2016, 1, 10)
        )
        with report_csv(date_range) as fd:
            report = fd.getvalue()

        blocked = Credential.objects.blocked()
        blocked = sorted(blocked.values_list('s3_key', flat=True))

        report_lines = report.split()
        assert len(report_lines) == 2
        assert '"{},{}"'.format(*blocked) in report_lines[1]
