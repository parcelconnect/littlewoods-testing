import datetime

import pytest
from freezegun import freeze_time

from idv.collector.const import CredentialStatus
from idv.collector.domain import create_credential
from idv.collector.models import Credential
from idv.mover.reporting import report_csv


@pytest.mark.django_db
class TestReportCsv:

    def test_headers(self, credentials):
        since = datetime.datetime(2016, 1, 2)
        until = datetime.datetime(2016, 1, 6)
        date_range = (since, until)
        with report_csv(date_range) as fd:
            content = fd.getvalue()
        content_lines = content.split()
        content_headers = content_lines[0]
        assert content_headers == ('"account_number","email","files_moved",'
                                   '"files_not_found"')

    def test_creation_date_filtering(self, credentials, other_account):
        with freeze_time('2016-01-10'):
            cred = create_credential(other_account, 'moved.jpg')
            cred.status = CredentialStatus.Moved.value
            cred.save()

            cred = create_credential(other_account, 'not_found.jpg')
            cred.status = CredentialStatus.NotFound.value
            cred.save()

        since = datetime.datetime(2016, 1, 1)
        until = datetime.datetime(2016, 1, 7)
        date_range = (since, until)
        with report_csv(date_range) as fd:
            report = fd.getvalue()

        report_lines = report.split()
        assert len(report_lines) == 2
        assert report_lines[1].startswith('"12345678"')

    def test_lists_moved(self, credentials, account):
        with freeze_time('2016-01-04'):
            cred = create_credential(account, 'moved-away.jpg')
            cred.status = CredentialStatus.Moved.value
            cred.save()

        since = datetime.datetime(2016, 1, 1)
        until = datetime.datetime(2016, 1, 10)
        date_range = (since, until)
        with report_csv(date_range) as fd:
            report = fd.getvalue()

        report_lines = report.split()
        account_line = report_lines[1]

        moved = Credential.objects.filter(
            status=CredentialStatus.Moved.value
        ).values_list('s3_key', flat=True)

        assert len(report_lines) == 2
        assert (
            ('"{},{}"'.format(moved[0], moved[1]) in account_line) or
            ('"{},{}"'.format(moved[0], moved[1]) in account_line)
        )

    def test_lists_not_found(self, not_found_credential, account):
        with freeze_time('2016-01-04'):
            cred = create_credential(account, 'not--found.jpg')
            cred.status = CredentialStatus.NotFound.value
            cred.save()

        since = datetime.datetime(2016, 1, 1)
        until = datetime.datetime(2016, 1, 10)
        date_range = (since, until)
        with report_csv(date_range) as fd:
            report = fd.getvalue()

        not_found = Credential.objects.filter(
            status=CredentialStatus.NotFound.value
        ).values_list('s3_key', flat=True)

        report_lines = report.split()
        account_line = report_lines[1]

        assert len(report_lines) == 2
        assert (
            ('"{},{}"'.format(not_found[0], not_found[1]) in account_line) or
            ('"{},{}"'.format(not_found[0], not_found[1]) in account_line)
        )
