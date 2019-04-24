from datetime import timedelta
from io import StringIO
from unittest.mock import patch

import pytest
from django.core import mail
from django.utils import timezone
from freezegun import freeze_time

from idv.mover.mail import _get_move_report_context, send_move_report


@pytest.mark.django_db
class TestSendMoveReport:

    @patch('idv.mover.mail.report_csv')
    def test_sends_expected_email_when_range_bigger_than_one_day(
            self, mock_report):
        mock_report.return_value = StringIO()

        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=7)

        send_move_report((start_date, end_date), ['brianhernandez@scurri.com'])

        s_date = start_date.strftime('%Y-%m-%d')
        e_date = end_date.strftime('%Y-%m-%d')
        report_file = mail.outbox[0].attachments[0]
        expected_subject = (
            f'Littlewoods ID&V Report for {s_date} - {e_date} (excluded)')
        s_date = start_date.strftime('%Y%m%d')
        e_date = end_date.strftime('%Y%m%d')
        expected_report_file = f'idv_report_{s_date}-{e_date}_excluded.csv'

        assert len(mail.outbox) == 1
        assert len(mail.outbox[0].attachments) == 1
        assert report_file[0] == expected_report_file
        assert mail.outbox[0].subject == expected_subject

    @patch('idv.mover.mail.report_csv')
    def test_sends_expected_email_when_range_equal_to_one_day(
            self, mock_report):
        mock_report.return_value = StringIO()

        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=1)

        send_move_report((start_date, end_date), ['brianhernandez@scurri.com'])

        s_date = start_date.strftime('%Y-%m-%d')
        report_file = mail.outbox[0].attachments[0]
        expected_subject = f'Littlewoods ID&V Report for {s_date}'
        s_date = start_date.strftime('%Y%m%d')
        expected_report_file = f'idv_report_{s_date}.csv'

        assert len(mail.outbox) == 1
        assert len(mail.outbox[0].attachments) == 1
        assert report_file[0] == expected_report_file
        assert mail.outbox[0].subject == expected_subject


@pytest.mark.django_db
class TestGetMoveReportContext:

    def test_returns_expected_context_when_no_credentials(self):
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=1)

        context = _get_move_report_context((start_date, end_date))

        expected_context = {
            'n_moved': 0,
            'n_not_found': 0
        }

        assert context == expected_context

    @freeze_time('2016-01-07 12:00')
    def test_returns_expected_context_when_credentials(self, credentials):
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=7)

        context = _get_move_report_context((start_date, end_date))

        expected_context = {
            'n_moved': 1,
            'n_not_found': 1
        }

        assert context == expected_context
