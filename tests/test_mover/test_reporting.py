from datetime import date, datetime

import pytest
from freezegun import freeze_time
from waffle.testutils import override_switch

from idv.collector.const import CredentialStatus
from idv.collector.domain import create_credential
from idv.mover.reporting import generate_report_csv_content, report_csv


@pytest.mark.django_db
class TestGenerateReportCsvContent:

    def test_returns_expected_rows(self, credentials):
        date_range = (
            datetime(2016, 1, 2),
            datetime(2016, 1, 6)
        )
        data = generate_report_csv_content(date_range)

        assert len(data) == 2
        assert data == [
            ['account_number', 'email', 'files_moved', 'files_not_found',
             'files_blocked'],
            ['12345678', 'account@littlewoods.ie', '', 'normal_12345678_3.jpg',
             'normal_12345678_6.exe']]

    @override_switch('lwi-new-design', active=True)
    def test_returns_hyphens_on_dates_when_min_date_and_switch_lwi_new_design_is_enabled(  # noqa
            self, credentials):
        date_range = (
            datetime(2016, 1, 2),
            datetime(2016, 1, 6)
        )
        data = generate_report_csv_content(date_range)

        assert len(data) == 2
        assert data == [
            ['account_number', 'email', 'files_moved', 'files_not_found',
             'files_blocked', 'proof_of_address_date_1',
             'proof_of_address_date_2'],
            ['12345678', 'account@littlewoods.ie', '', 'normal_12345678_3.jpg',
             'normal_12345678_6.exe', '-', '-']]

    @override_switch('lwi-new-design', active=True)
    def test_returns_dates_when_switch_lwi_new_design_is_enabled(
            self, credentials):
        for credential in credentials:
            credential.account.proof_of_address_date_1 = date(2016, 1, 1)
            credential.account.proof_of_address_date_2 = date(2015, 12, 31)
            credential.account.save()

        date_range = (
            datetime(2016, 1, 2),
            datetime(2016, 1, 6)
        )
        data = generate_report_csv_content(date_range)

        assert len(data) == 2
        assert data == [
            ['account_number', 'email', 'files_moved', 'files_not_found',
             'files_blocked', 'proof_of_address_date_1',
             'proof_of_address_date_2'],
            ['12345678', 'account@littlewoods.ie', '', 'normal_12345678_3.jpg',
             'normal_12345678_6.exe', '01/01/2016', '31/12/2015']]


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

    @override_switch('lwi-new-design', active=True)
    def test_headers_when_lwi_new_design_is_enabled(self, credentials):
        date_range = (
            datetime(2016, 1, 2),
            datetime(2016, 1, 6)
        )
        with report_csv(date_range) as fd:
            content = fd.getvalue()
        content_lines = content.split()
        content_headers = content_lines[0]
        assert content_headers == (
            '"account_number","email","files_moved","files_not_found",'
            '"files_blocked","proof_of_address_date_1",'
            '"proof_of_address_date_2"')

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

        report_lines = report.split()
        assert len(report_lines) == 2
        assert f'"{report_lines[1][0]},{report_lines[1][1]}"'

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

        report_lines = report.split()
        assert len(report_lines) == 2
        assert f'"{report_lines[1][0]},{report_lines[1][1]}"'

    def test_lists_blocked(self, blocked_credential, account):
        with freeze_time('2016-01-04'):
            create_credential(account, 'blocked2.exe', 'normal')

        date_range = (
            datetime(2016, 1, 1),
            datetime(2016, 1, 10)
        )
        with report_csv(date_range) as fd:
            report = fd.getvalue()

        report_lines = report.split()
        assert len(report_lines) == 2
        assert f'"{report_lines[1][0]},{report_lines[1][1]}"'
